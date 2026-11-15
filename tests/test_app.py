import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_participants = {
        name: list(activity["participants"])
        for name, activity in activities.items()
    }

    with TestClient(app) as test_client:
        yield test_client

    for name, participants in original_participants.items():
        activities[name]["participants"][:] = participants


def test_unregister_removes_participant(client):
    activity = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_rejects_participant_not_signed_up(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not-signed-up@mergington.edu"},
    )

    assert response.status_code == 404


def test_signup_appears_in_activity_list(client):
    activity = "Basketball Team"
    email = "new-student@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    assert signup_response.status_code == 200
    assert email in activities_response.json()[activity]["participants"]
