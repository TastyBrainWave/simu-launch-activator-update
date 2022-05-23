import os
from unittest import TestCase
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from sql_app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()



@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

android_studio_path = os.environ.get("ANDROID_STUDIO_PATH") or None

class TestEverything(TestCase):
    experience_name = "com.amazon.calculator.apk"

    def test_all_routes(self):

        response = client.get("/")
        assert response.status_code == 200

        response = client.post("/start", json={'devices': [], 'experience': self.experience_name}, headers={"Content-Type": "application/json"})
        assert response.status_code == 200

        response = client.post("/stop", json={'devices': [], 'experience': self.experience_name}, headers={"Content-Type": "application/json"})
        assert response.status_code == 200

        response = client.get("/devices")
        assert response.json()["devices"] == []

        response = client.post("/exit-server")
        assert response.status_code == 200

    def test_add_experience(self):
        response = client.post("/add-remote-experience", json={'devices': [], 'apk_name': self.experience_name, 'command': ''})
        assert response.status_code == 200
        assert response.json()["success"] == True

    def test_remove_experience(self):
        response = client.post("/remove-remote-experience", json={'devices': [], 'experience': self.experience_name})
        assert response.status_code == 200
        assert response.json()["success"] == True

#   def test_upload(self):
#       with open("com.nothing.nothing.apk", "rb") as f:
#           response = client.post("/upload", {"file": ("com.nothing.nothing.apk", f, ".apk"),'command': ''}, headers={"Content-Type": "multipart/form-data"})
#           print(response.json())
#           assert response.status_code == 200
