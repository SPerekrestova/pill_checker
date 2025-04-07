from unittest.mock import patch


def test_health_endpoint(client):
    """Test the health endpoint returns 200 OK"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model is loaded" in data["message"]


def test_extract_entities(client):
    """Test entity extraction with mock data"""
    response = client.post("/api/extract_entities", json={"text": "Test text"})
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert len(data["entities"]) > 0
    entity = data["entities"][0]
    assert entity["text"] == "Test text"
    assert len(entity["umls_entities"]) > 0
    umls_entity = entity["umls_entities"][0]
    assert umls_entity["canonical_name"] == "Test Entity"


def test_extract_entities_error_handling(client):
    """Test error handling during entity extraction"""
    with patch(
        "medical_ner.services.nlp.get_nlp_model",
        side_effect=Exception("Test exception"),
    ):
        response = client.post("/api/extract_entities", json={"text": "Test text"})
        assert response.status_code == 500
        assert "Error processing text" in response.json()["detail"]
