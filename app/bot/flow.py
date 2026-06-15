from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.core.content import Challenge, ChallengeBank
from app.core.quiz_engine import QuizEngine
from app.core.safety import SafetyChecker
from app.core.scoring import ScoringService
from app.db.models import User
from app.db.repository import Repository

BOT_DISPLAY_NAME = "FlagWarden"
SAFE_SCOPE = "legal CTF labs or systems you own or are authorized to test"


@dataclass(frozen=True)
class Button:
    label: str
    command: str


@dataclass(frozen=True)
class BotResponse:
    text: str
    buttons: list[Button] = field(default_factory=list)
    refused: bool = False


@dataclass
class FlowMetrics:
    handled_messages: int = 0
    safety_refusals: int = 0
    answers_checked: int = 0
    correct_answers: int = 0
    reports: int = 0

    def snapshot(self) -> dict[str, int]:
        return {
            "handled_messages": self.handled_messages,
            "safety_refusals": self.safety_refusals,
            "answers_checked": self.answers_checked,
            "correct_answers": self.correct_answers,
            "reports": self.reports,
        }


MAIN_MENU = [
    Button("Daily", "/daily"),
    Button("Challenge", "/challenge"),
    Button("Quiz", "/quiz"),
    Button("Score", "/score"),
    Button("Help", "/help"),
    Button("Safety", "/safety"),
]


class BotFlow:
    def __init__(
        self,
        challenge_bank: ChallengeBank,
        session_factory: sessionmaker[Session],
        settings: Settings,
        safety_checker: SafetyChecker | None = None,
        quiz_engine: QuizEngine | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.challenge_bank = challenge_bank
        self.session_factory = session_factory
        self.settings = settings
        self.safety_checker = safety_checker or SafetyChecker()
        self.quiz_engine = quiz_engine or QuizEngine()
        self.rng = rng or random.Random()
        self.metrics = FlowMetrics()

    def handle_text(
        self,
        platform: str,
        platform_user_id: str,
        text: str,
        display_name: str | None = None,
    ) -> BotResponse:
        self.metrics.handled_messages += 1
        normalized_text = (text or "").strip()
        if not normalized_text:
            return BotResponse("Send /help to see available commands.", buttons=MAIN_MENU)

        if len(normalized_text) > self.settings.input_max_length:
            return BotResponse(
                f"Please keep messages under {self.settings.input_max_length} characters."
            )

        with self.session_factory() as session:
            repo = Repository(session)
            user = repo.get_or_create_user(platform, platform_user_id, display_name)
            command, args = self._parse_command(normalized_text)

            if command in {"/answer", "/report"} and args:
                safety = self.safety_checker.check(args)
                if not safety.allowed:
                    self.metrics.safety_refusals += 1
                    return BotResponse(safety.message, refused=True)
            elif command is None:
                safety = self.safety_checker.check(normalized_text)
                if not safety.allowed:
                    self.metrics.safety_refusals += 1
                    return BotResponse(safety.message, refused=True)

            return self._dispatch(repo, user, command, args, normalized_text)

    def _parse_command(self, text: str) -> tuple[str | None, str]:
        if text.startswith("/"):
            command_part, _, args = text.partition(" ")
            command = command_part.split("@", maxsplit=1)[0].lower()
            return command, args.strip()

        first_word, _, rest = text.partition(" ")
        maybe_command = f"/{first_word.lower()}"
        if maybe_command in {
            "/start",
            "/help",
            "/categories",
            "/daily",
            "/quiz",
            "/challenge",
            "/hint",
            "/score",
            "/leaderboard",
            "/profile",
            "/safety",
        }:
            return maybe_command, rest.strip()
        return None, ""

    def _dispatch(
        self,
        repo: Repository,
        user: User,
        command: str | None,
        args: str,
        raw_text: str,
    ) -> BotResponse:
        if command == "/start":
            return self._start()
        if command == "/help":
            return self._help()
        if command == "/categories":
            return self._categories()
        if command == "/daily":
            return self._send_challenge(
                repo,
                user,
                self.challenge_bank.daily_challenge(),
                "Daily challenge",
            )
        if command in {"/quiz", "/challenge"}:
            solved = repo.solved_ids(user.id)
            challenge = self.challenge_bank.random_challenge(exclude_ids=solved, rng=self.rng)
            label = "Quiz mode" if command == "/quiz" else "Random challenge"
            return self._send_challenge(repo, user, challenge, label)
        if command == "/hint":
            return self._hint(repo, user)
        if command == "/answer":
            return self._answer(repo, user, args)
        if command == "/score":
            return self._score(user)
        if command == "/leaderboard":
            return self._leaderboard(repo)
        if command == "/profile":
            return self._profile(repo, user)
        if command == "/report":
            return self._report(repo, user, args)
        if command == "/safety":
            return self._safety()

        if command:
            return BotResponse(
                "I didn't recognize that command. Use /help to see available "
                "FlagWarden commands.",
                buttons=MAIN_MENU,
            )

        return BotResponse(
            "Send /challenge, /daily, or /help to continue learning with FlagWarden.",
            buttons=MAIN_MENU,
        )

    def _start(self) -> BotResponse:
        return BotResponse(
            "Welcome to FlagWarden 🛡️🏁\n\n"
            "Practice CTF cybersecurity safely with daily challenges, hints, "
            "scoring, streaks, and ethical safety guardrails.\n\n"
            "Use this bot only in legal CTF labs or systems you own or are "
            "authorized to test.\n\n"
            "Choose a button or send /help.",
            buttons=MAIN_MENU,
        )

    def _help(self) -> BotResponse:
        return BotResponse(
            f"{BOT_DISPLAY_NAME} commands:\n"
            "/start - Show welcome menu\n"
            "/help - Show available commands\n"
            "/daily - Get today's CTF challenge\n"
            "/challenge - Get a random challenge\n"
            "/quiz - Start quiz mode\n"
            "/hint - Get a hint for current challenge\n"
            "/answer <your answer> - Submit an answer\n"
            "/score - View score, solved challenges, and streak\n"
            "/profile - View progress by category\n"
            "/leaderboard - View top users\n"
            "/safety - Read the ethical use policy\n"
            "/categories - Browse challenge categories\n"
            "/report <feedback> - Report an issue or feedback",
            buttons=MAIN_MENU,
        )

    def _categories(self) -> BotResponse:
        counts = self.challenge_bank.counts_by_category()
        lines = ["CTF categories:"]
        for category in [
            "Web",
            "Forensics",
            "Crypto Basics",
            "Linux",
            "Networking",
            "OSINT Basics",
            "Secure Coding",
        ]:
            lines.append(f"- {category}: {counts.get(category, 0)} challenges")
        return BotResponse("\n".join(lines), buttons=MAIN_MENU)

    def _send_challenge(
        self,
        repo: Repository,
        user: User,
        challenge: Challenge,
        label: str,
    ) -> BotResponse:
        repo.set_current_challenge(user, challenge.id)
        return BotResponse(
            f"{label}\n"
            f"Title: {challenge.title}\n"
            f"Category: {challenge.category}\n"
            f"Difficulty: {challenge.difficulty}\n"
            f"Points: {challenge.points}\n\n"
            f"{challenge.prompt}\n\n"
            "Submit: /answer <your answer>\n"
            "Need help? Send /hint.",
            buttons=[
                Button("Hint", "/hint"),
                Button("Answer", "/answer "),
                Button("Score", "/score"),
            ],
        )

    def _hint(self, repo: Repository, user: User) -> BotResponse:
        if not user.current_challenge_id:
            return BotResponse(
                "No active challenge yet. Start with /challenge or /daily.",
                buttons=MAIN_MENU,
            )

        challenge = self.challenge_bank.get(user.current_challenge_id)
        if not challenge:
            repo.clear_current_challenge(user)
            return BotResponse(
                "That challenge is no longer available. Use /challenge for a new one."
            )

        if user.hints_used >= len(challenge.hints):
            return BotResponse(
                "No more hints are available for this challenge. Try /answer <text> or /challenge."
            )

        hint_number = user.hints_used + 1
        hint = challenge.hints[user.hints_used]
        repo.increment_hint(user)
        preview = ScoringService.preview(challenge.points, hint_number)
        return BotResponse(
            f"Hint {hint_number}/{len(challenge.hints)}: {hint}\n"
            f"Current max score for this challenge: {preview.points_awarded} points."
        )

    def _answer(self, repo: Repository, user: User, answer: str) -> BotResponse:
        if not answer:
            return BotResponse(
                "Usage: /answer <your answer>\n"
                "Example: /answer flag{example}"
            )
        if not user.current_challenge_id:
            return BotResponse(
                "No active challenge yet. Start with /challenge or /daily.",
                buttons=MAIN_MENU,
            )

        cutoff = datetime.now(UTC) - timedelta(
            seconds=self.settings.answer_rate_limit_window_seconds
        )
        if repo.recent_submission_count(user, cutoff) >= self.settings.answer_rate_limit_count:
            return BotResponse(
                "You're submitting answers very quickly. Take a short pause, then try again."
            )

        challenge = self.challenge_bank.get(user.current_challenge_id)
        if not challenge:
            repo.clear_current_challenge(user)
            return BotResponse(
                "That challenge is no longer available. Use /challenge for a new one."
            )

        result = self.quiz_engine.check_answer(challenge, answer)
        self.metrics.answers_checked += 1
        repo.record_submission(user, challenge.id, answer, result.correct)

        if not result.correct:
            return BotResponse(
                "Not quite. Try again, or use /hint if you need a clue."
            )

        self.metrics.correct_answers += 1
        hints_used = user.hints_used
        already_solved = repo.has_solved(user.id, challenge.id)
        if already_solved:
            repo.clear_current_challenge(user)
            return BotResponse(
                "Correct — flag captured! 🏁\n"
                f"Answer: {challenge.answer}\n"
                "Already solved. No extra points were added.\n\n"
                f"Explanation: {result.explanation}",
                buttons=MAIN_MENU,
            )

        points = ScoringService.calculate_points(challenge.points, hints_used)
        repo.mark_solved(user, challenge.id, challenge.category, points, hints_used)
        repo.clear_current_challenge(user)
        return BotResponse(
            "Correct — flag captured! 🏁\n"
            f"Answer: {challenge.answer}\n"
            f"Points awarded: {points}\n"
            f"Total score: {user.score}\n\n"
            f"Explanation: {result.explanation}\n\n"
            f"Safety note: {challenge.safety_note}",
            buttons=MAIN_MENU,
        )

    def _score(self, user: User) -> BotResponse:
        return BotResponse(
            "FlagWarden Score\n"
            f"Score: {user.score} points\n"
            f"Solved: {user.solved_count} challenge(s)\n"
            f"Streak: {user.streak} day(s)",
            buttons=MAIN_MENU,
        )

    def _leaderboard(self, repo: Repository) -> BotResponse:
        leaders = repo.leaderboard(limit=10)
        if not leaders:
            return BotResponse("No scores yet. Solve a challenge with /challenge.")

        lines = ["Leaderboard:"]
        for index, leader in enumerate(leaders, start=1):
            name = leader.display_name or f"{leader.platform}:{leader.platform_user_id}"
            lines.append(f"{index}. {name} - {leader.score} pts ({leader.solved_count} solved)")
        return BotResponse("\n".join(lines), buttons=MAIN_MENU)

    def _profile(self, repo: Repository, user: User) -> BotResponse:
        solved = repo.category_progress(user.id)
        totals = self.challenge_bank.counts_by_category()
        lines = [
            f"Profile for {user.display_name or user.platform_user_id}",
            f"Score: {user.score} | Streak: {user.streak} day(s)",
            "Progress by category:",
        ]
        for category in sorted(totals):
            lines.append(f"- {category}: {solved.get(category, 0)}/{totals[category]}")
        return BotResponse("\n".join(lines), buttons=MAIN_MENU)

    def _report(self, repo: Repository, user: User, args: str) -> BotResponse:
        if not args:
            return BotResponse("Use /report <what went wrong or could be improved>.")
        challenge_id = user.current_challenge_id
        repo.save_report(user, args[:1000], challenge_id=challenge_id)
        self.metrics.reports += 1
        return BotResponse("Thanks. Your report was saved for review.", buttons=MAIN_MENU)

    def _safety(self) -> BotResponse:
        return BotResponse(
            "Ethical use policy:\n"
            "- FlagWarden is designed for ethical CTF learning only.\n"
            f"- Use it only in {SAFE_SCOPE}.\n"
            "- I help with CTF practice, defensive learning, and safe cybersecurity concepts.\n"
            "- I refuse real-target hacking, credential theft, phishing, malware, persistence, "
            "evasion, public-IP scanning, and access-control bypass requests.\n"
            "- I can help reframe risky questions into safe lab or defensive learning tasks.",
            buttons=MAIN_MENU,
        )
