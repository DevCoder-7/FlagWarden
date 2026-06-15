from __future__ import annotations

from app.db.repository import Repository


def test_repository_user_progress_and_no_double_score(session_factory):
    with session_factory() as session:
        repo = Repository(session)
        user = repo.get_or_create_user("telegram", "123", "Learner")
        repo.set_current_challenge(user, "web-001-status-404")
        repo.increment_hint(user)
        repo.record_submission(user, "web-001-status-404", "not found", True)

        assert repo.mark_solved(user, "web-001-status-404", "Web", 38, user.hints_used) is True
        assert user.score == 38
        assert user.solved_count == 1
        assert repo.has_solved(user.id, "web-001-status-404") is True

        assert repo.mark_solved(user, "web-001-status-404", "Web", 38, user.hints_used) is False
        assert user.score == 38
        assert user.solved_count == 1


def test_repository_category_progress_and_reports(session_factory):
    with session_factory() as session:
        repo = Repository(session)
        user = repo.get_or_create_user("telegram", "555")
        repo.mark_solved(user, "linux-001-permissions-644", "Linux", 50, 0)
        report = repo.save_report(user, "The hint could be clearer.", "linux-001-permissions-644")

        assert report.id is not None
        assert repo.category_progress(user.id) == {"Linux": 1}
