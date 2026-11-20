"""Tests for the /health and basic /records endpoints."""



class TestHealth:
    def test_health_returns_ok(self, api_client):
        response = api_client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "uptime_seconds" in body


class TestRecords:
    def test_list_records_returns_list(self, api_client):
        response = api_client.get("/records")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    def test_list_records_with_limit(self, api_client):
        response = api_client.get("/records?limit=2")
        assert response.status_code == 200
        assert len(response.json()) <= 2

    def test_get_record_by_id_first(self, api_client):
        response = api_client.get("/records/1")
        assert response.status_code == 200
        data = response.json()
        assert "loan_category" in data

    def test_get_record_invalid_id_returns_404(self, api_client):
        response = api_client.get("/records/99999")
        assert response.status_code == 404

    def test_search_returns_results(self, api_client):
        response = api_client.get("/search?q=Shishu")
        assert response.status_code == 200
        body = response.json()
        assert "results" in body
        assert isinstance(body["results"], list)

    def test_search_missing_query_returns_422(self, api_client):
        response = api_client.get("/search")
        assert response.status_code == 422
