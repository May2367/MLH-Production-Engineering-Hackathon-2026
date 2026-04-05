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


def test_list_urls_page_out_of_range(client):
    response = client.get("/urls?page=9999")
    assert response.status_code == 200
    assert response.get_json() == []


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
    response = client.post("/urls", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 201
    data = response.get_json()
    assert data["short_code"] == "NEWCODE"


def test_create_url_missing_field(client, sample_user):
    payload = {"user_id": "999"}  # missing original_url
    response = client.post("/urls", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_url_invalid_json(client):
    response = client.post("/urls", data="notjson", content_type="application/json")
    assert response.status_code == 400


def test_redirect_active(client, sample_url):
    response = client.get(f"/{sample_url.short_code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == sample_url.original_url


def test_redirect_inactive(client, sample_url):
    sample_url.is_active = False
    sample_url.save()
    response = client.get(f"/{sample_url.short_code}", follow_redirects=False)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_update_url_empty_payload(client, sample_url):
    response = client.put(f"/urls/{sample_url.id}", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_delete_url(client, sample_url):
    response = client.delete(f"/urls/{sample_url.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


def test_delete_url_not_found(client):
    response = client.delete("/urls/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


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


def test_create_user_missing_field(client):
    payload = {"username": "bob"}  # missing email
    response = client.post("/users", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_user_empty_payload(client, sample_user):
    response = client.put(f"/users/{sample_user.id}", json={})
    assert response.status_code == 400
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


def test_create_event_missing_field(client):
    payload = {"url_id": 1, "user_id": 1}  # missing event_type
    response = client.post("/events", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_bulk_load_events_missing_file(client):
    response = client.post("/events/bulk", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_bulk_load_events_file_not_found(client):
    response = client.post("/events/bulk", json={"file": "fake.csv"})
    assert response.status_code == 404
    assert "error" in response.get_json()


# ── Metrics endpoint ─────────────────────────────────────────────────────────

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert "cpu" in data
    assert "percent_used" in data["cpu"]
    assert "disk" in data
    assert "memory" in data
