import os
os.environ["DATABASE_URL"]="sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"]="test-secret"
from fastapi.testclient import TestClient
from app.database import Base,engine
from app.main import app
import pytest
@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with TestClient(app) as c: yield c
    Base.metadata.drop_all(bind=engine)
