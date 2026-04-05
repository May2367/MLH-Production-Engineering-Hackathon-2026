import pytest
from app import create_app
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.events import Event

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_tables([User, Url, Event], safe=True)
        
        yield app
        
        db.drop_tables([Event, Url, User])


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User.create(
            username="testuser",
            email="test@example.com",
            created_at="2024-01-01 00:00:00"
        )
        return user


@pytest.fixture
def sample_url(app, sample_user):
    with app.app_context():
        url = Url.create(
            user_id=sample_user.id,
            short_code="TESTCODE",
            original_url="https://example.com",
            title="Test URL",
            is_active=True,
            created_at="2024-01-01 00:00:00",
            updated_at="2024-01-01 00:00:00"
        )
        return url
