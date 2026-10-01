import time


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant that drafts legal-document templates.

Your job is to produce a structured, professional DRAFT based only on the user's supplied facts.
Do not invent names, dates, addresses, amounts, obligations, statutes, court cases, citations,
jurisdictions, or legal rights that were not supplied.

Rules:
- Clearly label the result as a DRAFT.
- Use neutral formal legal language.
- Organize the document with a title and numbered sections.
- Include the parties and effective date exactly as provided.
- Convert semicolon-separated terms into appropriate clauses.
- If a material fact is missing, use [TO BE COMPLETED] rather than guessing.
- Do not claim the document is legally valid, legally sound, or attorney-reviewed.
- Do not provide a legal conclusion about a dispute.
- Finish with signature blocks appropriate to the identified parties.
- Avoid Markdown tables because the application creates its own export formatting.
"""


class GeminiDocumentGenerator:
    def __init__(self, api_key: str, model: str):
        # Lazy import keeps non-AI API/export tests runnable even when the Gemini
        # package is not installed in the current test environment.
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "The Gemini SDK is not installed. Run: pip install -r requirements.txt"
            ) from exc

        self.types = types
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        language: str = "English",
    ) -> str:

        prompt = f"""
Create a {document_type} draft.

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

OUTPUT LANGUAGE:
{language}

Write a complete, editable draft. Preserve all user-provided facts.
"""

        # Retry temporary Gemini service failures.
        #
        # These errors can occur when the Gemini service is temporarily
        # overloaded. We wait progressively longer between attempts.
        max_attempts = 4
        retry_delays = [5, 10, 20]

        last_error = None

        for attempt in range(max_attempts):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=self.types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2,
                        max_output_tokens=8192,
                    ),
                )

                text = (response.text or "").strip()

                if not text:
                    raise RuntimeError("Gemini returned an empty response.")

                return text

            except Exception as exc:
                last_error = exc

                error_text = str(exc)

                # Only retry errors that are normally temporary.
                is_retryable = any(
                    error_code in error_text
                    for error_code in (
                        "503",
                        "429",
                        "500",
                        "502",
                        "504",
                        "UNAVAILABLE",
                        "RESOURCE_EXHAUSTED",
                        "INTERNAL",
                    )
                )

                # Do not retry permanent errors such as invalid API keys,
                # invalid model names, malformed requests, etc.
                if not is_retryable:
                    raise RuntimeError(
                        f"Gemini document generation failed: {exc}"
                    ) from exc

                # If this was the final attempt, return a clean error.
                if attempt == max_attempts - 1:
                    raise RuntimeError(
                        "Gemini is temporarily unavailable after multiple attempts. "
                        "Please wait a little while and try generating the document again."
                    ) from exc

                # Wait before the next attempt.
                time.sleep(retry_delays[attempt])

        # Safety fallback; normally unreachable.
        raise RuntimeError(
            f"Gemini document generation failed: {last_error}"
        ) from last_error