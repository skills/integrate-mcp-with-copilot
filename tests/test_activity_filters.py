import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app

client = TestClient(app)


def test_get_activities_can_filter_by_category():
    response = client.get("/activities", params={"category": "Sports"})

    assert response.status_code == 200
    data = response.json()
    assert list(data.keys()) == ["Basketball Team", "Gym Class", "Soccer Team"]


def test_get_activities_can_search_by_name():
    response = client.get("/activities", params={"search": "chess"})

    assert response.status_code == 200
    data = response.json()
    assert list(data.keys()) == ["Chess Club"]


def test_get_activities_can_sort_by_name():
    response = client.get("/activities", params={"sort": "name"})

    assert response.status_code == 200
    data = response.json()
    assert list(data.keys())[:3] == ["Art Club", "Basketball Team", "Chess Club"]
