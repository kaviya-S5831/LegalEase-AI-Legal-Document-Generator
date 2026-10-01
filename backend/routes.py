from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .ai_core.gemini_generator import GeminiDocumentGenerator
from .config import get_settings
from .dependencies import require_gemini_key
from .schemas import DocumentRequest, ExportRequest
from .services.document_export import (
    format_docx,
    format_pdf,
    format_txt,
    safe_filename,
)

router = APIRouter()


@router.post("/generate")
def generate_document(request: DocumentRequest):
    settings = get_settings()
    api_key = require_gemini_key()

    try:
        generator = GeminiDocumentGenerator(
            api_key=api_key,
            model=settings.gemini_model,
        )
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            language=request.language,
        )
        if len(content) > settings.max_document_chars:
            raise HTTPException(status_code=502, detail="Generated document exceeded the configured size limit.")
        return {
            "document_type": request.document_type,
            "content": content,
            "model": settings.gemini_model,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Document generation failed: {exc}") from exc


@router.post("/export/txt")
def export_txt(request: ExportRequest):
    data = format_txt(request.content)
    return Response(
        content=data,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename(request.document_type, "txt")}"'},
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):
    try:
        data = format_docx(request.content, request.document_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DOCX export failed: {exc}") from exc

    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename(request.document_type, "docx")}"'},
    )


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):
    try:
        data = format_pdf(request.content, request.document_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {exc}") from exc

    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename(request.document_type, "pdf")}"'},
    )
