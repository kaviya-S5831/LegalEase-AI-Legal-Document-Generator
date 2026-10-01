from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=200)
    parties: str = Field(..., min_length=2, max_length=10000)
    terms: str = Field(..., min_length=2, max_length=20000)
    effective_date: str = Field(..., min_length=2, max_length=100)
    language: str = Field(default="English", min_length=2, max_length=50)

    @field_validator("document_type", "parties", "terms", "effective_date", "language")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class ExportRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=200)
    content: str = Field(..., min_length=20, max_length=200000)

    @field_validator("document_type", "content")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value
