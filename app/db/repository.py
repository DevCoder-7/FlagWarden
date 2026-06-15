from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.scoring import ScoringService
from app.db.models import Base, FeedbackReport, SolvedChallenge, Submission, User, utc_now


def build_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    if engine.url.get_backend_name() == "sqlite" and engine.url.database:
        database_path = engine.url.database
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


class Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_user(
        self,
        platform: str,
        platform_user_id: str,
        display_name: str | None = None,
    ) -> User:
        stmt = select(User).where(
            User.platform == platform,
            User.platform_user_id == platform_user_id,
        )
        user = self.session.execute(stmt).scalar_one_or_none()
        if user:
            if display_name and display_name != user.display_name:
                user.display_name = display_name
                user.updated_at = utc_now()
                self.session.commit()
            return user

        user = User(
            platform=platform,
            platform_user_id=platform_user_id,
            display_name=display_name,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def set_current_challenge(self, user: User, challenge_id: str) -> None:
        user.current_challenge_id = challenge_id
        user.hints_used = 0
        user.attempts_current = 0
        user.updated_at = utc_now()
        self.session.commit()

    def clear_current_challenge(self, user: User) -> None:
        user.current_challenge_id = None
        user.hints_used = 0
        user.attempts_current = 0
        user.updated_at = utc_now()
        self.session.commit()

    def increment_hint(self, user: User) -> int:
        user.hints_used += 1
        user.updated_at = utc_now()
        self.session.commit()
        return user.hints_used

    def record_submission(
        self,
        user: User,
        challenge_id: str,
        answer: str,
        is_correct: bool,
    ) -> Submission:
        user.attempts_current += 1
        user.updated_at = utc_now()
        submission = Submission(
            user_id=user.id,
            challenge_id=challenge_id,
            answer=answer,
            is_correct=is_correct,
        )
        self.session.add(submission)
        self.session.commit()
        self.session.refresh(submission)
        return submission

    def recent_submission_count(self, user: User, since: datetime) -> int:
        stmt = (
            select(func.count(Submission.id))
            .where(Submission.user_id == user.id)
            .where(Submission.created_at >= since)
        )
        return int(self.session.execute(stmt).scalar_one())

    def has_solved(self, user_id: int, challenge_id: str) -> bool:
        stmt = select(SolvedChallenge.id).where(
            SolvedChallenge.user_id == user_id,
            SolvedChallenge.challenge_id == challenge_id,
        )
        return self.session.execute(stmt).first() is not None

    def mark_solved(
        self,
        user: User,
        challenge_id: str,
        category: str,
        points_awarded: int,
        hints_used: int,
    ) -> bool:
        if self.has_solved(user.id, challenge_id):
            return False

        solved = SolvedChallenge(
            user_id=user.id,
            challenge_id=challenge_id,
            category=category,
            points_awarded=points_awarded,
            hints_used=hints_used,
            attempts=max(1, user.attempts_current),
        )
        today = date.today()
        user.score += points_awarded
        user.solved_count += 1
        user.streak = ScoringService.next_streak(user.last_solved_on, user.streak, today=today)
        user.last_solved_on = today
        user.updated_at = utc_now()
        self.session.add(solved)
        self.session.commit()
        return True

    def category_progress(self, user_id: int) -> dict[str, int]:
        stmt = (
            select(SolvedChallenge.category, func.count(SolvedChallenge.id))
            .where(SolvedChallenge.user_id == user_id)
            .group_by(SolvedChallenge.category)
        )
        return {category: int(count) for category, count in self.session.execute(stmt).all()}

    def leaderboard(self, limit: int = 10) -> list[User]:
        stmt = (
            select(User)
            .order_by(User.score.desc(), User.solved_count.desc(), User.updated_at.asc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def solved_ids(self, user_id: int) -> set[str]:
        stmt = select(SolvedChallenge.challenge_id).where(SolvedChallenge.user_id == user_id)
        return {challenge_id for (challenge_id,) in self.session.execute(stmt).all()}

    def save_report(
        self,
        user: User,
        message: str,
        challenge_id: str | None = None,
    ) -> FeedbackReport:
        report = FeedbackReport(
            user_id=user.id,
            challenge_id=challenge_id,
            message=message,
        )
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    def solved_summary(self, user_id: int) -> Iterable[SolvedChallenge]:
        stmt = select(SolvedChallenge).where(SolvedChallenge.user_id == user_id)
        return self.session.execute(stmt).scalars().all()
