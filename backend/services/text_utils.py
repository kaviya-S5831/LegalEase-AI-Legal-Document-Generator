import html
import re


def sanitize_text(text: str) -> str:
    """Normalize common typography while retaining useful document punctuation."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def terms_from_semicolon_text(terms: str) -> list[str]:
    return [item.strip() for item in terms.split(";") if item.strip()]


def text_to_html(text: str) -> str:
    escaped = html.escape(text)
    blocks = []
    for paragraph in escaped.split("\n\n"):
        paragraph = paragraph.replace("\n", "<br>")
        if re.match(r"^(?:SECTION|ARTICLE|\d+[\.)]|[A-Z][A-Z\s/&-]{4,}:)", paragraph):
            blocks.append(f"<h3>{paragraph}</h3>")
        else:
            blocks.append(f"<p>{paragraph}</p>")
    return "\n".join(blocks)
