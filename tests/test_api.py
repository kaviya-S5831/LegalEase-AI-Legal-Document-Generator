from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_export_txt():
    response = client.post(
        "/export/txt",
        json={"document_type": "NDA", "content": "This is a legal draft."},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")


def test_generate_without_key_returns_service_error(monkeypatch):
    from backend import dependencies

    monkeypatch.setattr(dependencies, "require_gemini_key", lambda: (_ for _ in ()).throw(
        __import__("fastapi").HTTPException(status_code=503, detail="Missing key")
    ))

    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": "A and B",
            "terms": "Confidentiality",
            "effective_date": "2026-10-01",
            "language": "English",
        },
    )
    assert response.status_code == 503
