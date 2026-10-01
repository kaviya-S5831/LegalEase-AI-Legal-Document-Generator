import html
import os
from datetime import date

import requests
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# =========================================================
# BACKEND CONFIG
# =========================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #9aa4b2;
        margin-bottom: 24px;
    }

    .preview {
        background: #111827;
        color: #e5e7eb;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 28px;
        min-height: 420px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.65;
        white-space: normal;
    }

    .warning {
        background: #3b2f12;
        color: #fde68a;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #6b5215;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered legal document drafting, editing, and export'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="warning">'
    '<b>Draft only:</b> AI-generated documents are not a substitute '
    'for legal advice. Review the final document with a qualified '
    'legal professional before signing or filing.'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = "Freelance Work Contract"

if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None

if "docx_data" not in st.session_state:
    st.session_state.docx_data = None

if "txt_data" not in st.session_state:
    st.session_state.txt_data = None


# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns(
    [0.95, 1.35],
    gap="large",
)


# =========================================================
# LEFT SIDE - DOCUMENT INPUT
# =========================================================

with left:

    st.subheader("Document details")

    document_type = st.text_input(
        "Document type",
        value=st.session_state.document_type,
        placeholder=(
            "e.g. NDA, Lease Agreement, "
            "Employment Contract"
        ),
    )

    parties = st.text_area(
        "Parties involved",
        height=110,
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
    )

    terms = st.text_area(
        "Terms & Conditions",
        height=180,
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        help="Separate clauses with semicolons.",
    )

    effective_date = st.text_input(
        "Effective date",
        value=str(date.today()),
        placeholder="2026-10-01",
    )

    language = st.selectbox(
        "Output language",
        [
            "English",
            "Tamil",
            "Hindi",
            "Malayalam",
            "Telugu",
            "Kannada",
        ],
    )

    # -----------------------------------------------------
    # GENERATE DOCUMENT
    # -----------------------------------------------------

    if st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    ):

        if not all(
            [
                document_type.strip(),
                parties.strip(),
                terms.strip(),
                effective_date.strip(),
            ]
        ):

            st.error(
                "Please complete document type, parties, "
                "terms, and effective date."
            )

        else:

            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "effective_date": effective_date,
                "language": language,
            }

            try:

                with st.spinner(
                    "Generating your draft with Gemini..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=180,
                    )

                if response.ok:

                    body = response.json()

                    st.session_state.document_type = (
                        document_type
                    )

                    st.session_state.document = (
                        body["content"]
                    )

                    # Clear old export files.
                    st.session_state.pdf_data = None
                    st.session_state.docx_data = None
                    st.session_state.txt_data = None

                    st.success(
                        "Draft generated using "
                        f"{body.get('model', 'Gemini')}."
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Could not reach FastAPI at "
                    f"{BACKEND_URL}: {exc}"
                )


# =========================================================
# RIGHT SIDE - PREVIEW + EXPORT
# =========================================================

with right:

    st.subheader("Editable preview")

    if st.session_state.document:

        # -------------------------------------------------
        # EDITABLE DOCUMENT
        # -------------------------------------------------

        edited = st.text_area(
            "Edit generated document",
            value=st.session_state.document,
            height=420,
            label_visibility="collapsed",
        )

        # Detect edits.
        if edited != st.session_state.document:

            st.session_state.document = edited

            # Existing exports are now outdated.
            st.session_state.pdf_data = None
            st.session_state.docx_data = None
            st.session_state.txt_data = None

        # -------------------------------------------------
        # PREVIEW
        # -------------------------------------------------

        preview_html = (
            html.escape(
                st.session_state.document
            )
            .replace("\n", "<br>")
        )

        st.markdown(
            f'<div class="preview">{preview_html}</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown("**Export**")

        payload = {
            "document_type": st.session_state.document_type,
            "content": st.session_state.document,
        }

        filename_base = (
            st.session_state.document_type
            .strip()
            .replace(" ", "_")
        )

        c1, c2, c3 = st.columns(3)


        # =================================================
        # TXT EXPORT
        # =================================================

        with c1:

            if st.button(
                "⚙️ Prepare TXT",
                use_container_width=True,
                key="prepare_txt",
            ):

                try:

                    with st.spinner(
                        "Preparing TXT..."
                    ):

                        r = requests.post(
                            f"{BACKEND_URL}/export/txt",
                            json=payload,
                            timeout=30,
                        )

                    if r.ok:

                        st.session_state.txt_data = (
                            bytes(r.content)
                        )

                        st.success(
                            "TXT ready."
                        )

                    else:

                        try:
                            detail = r.json().get(
                                "detail",
                                r.text,
                            )
                        except Exception:
                            detail = r.text

                        st.error(
                            f"TXT export failed: {detail}"
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"Backend unavailable: {exc}"
                    )

            # Download button is separate.
            if st.session_state.txt_data:

                st.download_button(
                    "⬇️ Download TXT",
                    data=st.session_state.txt_data,
                    file_name=f"{filename_base}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    on_click="ignore",
                    key="download_txt",
                )


        # =================================================
        # DOCX EXPORT
        # =================================================

        with c2:

            if st.button(
                "⚙️ Prepare DOCX",
                use_container_width=True,
                key="prepare_docx",
            ):

                try:

                    with st.spinner(
                        "Preparing DOCX..."
                    ):

                        r = requests.post(
                            f"{BACKEND_URL}/export/docx",
                            json=payload,
                            timeout=30,
                        )

                    if r.ok:

                        st.session_state.docx_data = (
                            bytes(r.content)
                        )

                        st.success(
                            "DOCX ready."
                        )

                    else:

                        try:
                            detail = r.json().get(
                                "detail",
                                r.text,
                            )
                        except Exception:
                            detail = r.text

                        st.error(
                            f"DOCX export failed: {detail}"
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"Backend unavailable: {exc}"
                    )

            # Download button is separate.
            if st.session_state.docx_data:

                st.download_button(
                    "⬇️ Download DOCX",
                    data=st.session_state.docx_data,
                    file_name=f"{filename_base}.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    use_container_width=True,
                    on_click="ignore",
                    key="download_docx",
                )


        # =================================================
        # PDF EXPORT
        # =================================================

        with c3:

            # ---------------------------------------------
            # PREPARE PDF
            # ---------------------------------------------

            if st.button(
                "⚙️ Prepare PDF",
                use_container_width=True,
                key="prepare_pdf",
            ):

                try:

                    with st.spinner(
                        "Preparing PDF..."
                    ):

                        r = requests.post(
                            f"{BACKEND_URL}/export/pdf",
                            json=payload,
                            timeout=30,
                        )

                    if r.ok:

                        # Store PDF bytes in session state.
                        st.session_state.pdf_data = (
                            bytes(r.content)
                        )

                        st.success(
                            f"PDF ready "
                            f"({len(r.content):,} bytes)."
                        )

                    else:

                        try:
                            detail = r.json().get(
                                "detail",
                                r.text,
                            )
                        except Exception:
                            detail = r.text

                        st.error(
                            f"PDF export failed: {detail}"
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"Backend unavailable: {exc}"
                    )

            # ---------------------------------------------
            # DOWNLOAD PDF
            # ---------------------------------------------

            if st.session_state.pdf_data:

                st.download_button(
                    "⬇️ Download PDF",
                    data=st.session_state.pdf_data,
                    file_name=f"{filename_base}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    on_click="ignore",
                    key="download_pdf",
                )

    else:

        st.info(
            "Your generated document will appear here. "
            "Enter the details and click Generate Document."
        )