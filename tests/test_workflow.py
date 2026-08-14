def h(user_id):
    return {"X-Debug-Telegram-Id": str(user_id)}


def challenge_payload():
    return {
        "id": "workflow-001",
        "title": "Workflow Test Challenge",
        "category": "test",
        "difficulty": "easy",
        "status": "draft",
        "version": "1.0.0",
        "author": "tester",
        "reviewer": None,
        "learning_objectives": ["Verify author-reviewer-admin separation."],
        "skills": ["platform.rbac"],
        "points": 100,
        "hints": [{"cost": 10, "text": "Check the state machine."}],
        "verifier": {"type": "quiz_choice", "choices": ["yes", "no"], "correct_index": 0},
        "safety": {"scope": "concept_only", "notes": "test"},
        "debrief": {
            "concept": "RBAC",
            "why_it_works": "Separation of duties reduces unilateral publication risk.",
            "remediation": "Use explicit role gates.",
            "references": [],
        },
    }


def test_author_reviewer_admin_workflow(client):
    created = client.post("/api/admin/drafts", headers=h(10003), json={"challenge": challenge_payload()})
    assert created.status_code == 200
    draft_id = created.json()["id"]
    assert created.json()["status"] == "DRAFT"

    submitted = client.post(f"/api/admin/drafts/{draft_id}/submit", headers=h(10003))
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "IN_REVIEW"

    assert client.post(f"/api/admin/drafts/{draft_id}/approve", headers=h(10003)).status_code == 403
    approved = client.post(f"/api/admin/drafts/{draft_id}/approve", headers=h(10002))
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    published = client.post(f"/api/admin/drafts/{draft_id}/publish", headers=h(10001))
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"
