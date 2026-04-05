import json


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check(client):
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] == "ok"


# ── URL routes ────────────────────────────────────────────────────────────────

def test_list_urls_empty(client):
    response = client.get("/urls")
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_urls_with_data(client, sample_url):
    response = client.get("/urls")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["short_code"] == "TESTCODE"


def test_get_url_by_id(client, sample_url):
    response = client.get(f"/urls/{sample_url.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["short_code"] == "TESTCODE"
    assert data["original_url"] == "https://example.com"


def test_get_url_not_found(client):
    response = client.get("/urls/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_create_url(client, sample_user):
    payload = {
        "user_id": sample_user.id,
        "short_code": "NEWCODE",
        "original_url": "https://newsite.com",
        "title": "New Site"
    }
    response = client.post(
        "/urls",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["short_code"] == "NEWCODE"


def test_create_url_missing_field(client, sample_user):
    payload = {
        "user_id": "999",
        "short_code": "NEWCODE"
        # original_url intentionally missing
    }
    response = client.post(
        "/urls",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


# ── User routes ───────────────────────────────────────────────────────────────

def test_list_users_empty(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_users_with_data(client, sample_user):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"


def test_get_user_by_id(client, sample_user):
    response = client.get(f"/users/{sample_user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ── Event routes ──────────────────────────────────────────────────────────────

def test_list_events_empty(client):
    response = client.get("/events")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_event_not_found(client):
    response = client.get("/events/99999")
    assert response.status_code == 404
    assert "error" in response.get_json()
