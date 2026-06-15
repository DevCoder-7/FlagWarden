from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass

REFUSAL_MESSAGE = (
    "I can't help with that because it could enable harm or unauthorized access. "
    "Use only in legal CTF labs or systems you own or are authorized to test. "
    "I can help reframe this as a toy CTF scenario, a defensive checklist, or a "
    "conceptual explanation."
)


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    categories: tuple[str, ...] = ()
    reason: str = ""
    message: str = ""


@dataclass(frozen=True)
class SafetyRule:
    category: str
    reason: str
    pattern: re.Pattern[str]


class SafetyChecker:
    def __init__(self) -> None:
        self._rules = [
            SafetyRule(
                "credential_theft",
                "Requests to steal, dump, harvest, or exfiltrate credentials are disallowed.",
                re.compile(
                    r"\b(steal|dump|harvest|exfiltrate|grab|capture)\b.{0,80}"
                    r"\b(passwords?|credentials?|tokens?|cookies?|sessions?)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "phishing",
                "Phishing pages, fake login flows, and credential collection are disallowed.",
                re.compile(
                    r"\b(create|make|build|host|send|write)\b.{0,80}"
                    r"\b(phishing|fake login|credential capture|credential harvesting)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "malware",
                "Malware, keyloggers, ransomware, backdoors, and destructive payloads "
                "are disallowed.",
                re.compile(
                    r"\b(write|build|create|deploy|install|spread|hide|obfuscate|compile)\b.{0,80}"
                    r"\b(malware|ransomware|keylogger|trojan|backdoor|destructive payload|rat)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "persistence_or_evasion",
                "Persistence, evasion, stealth, and security-tool bypass guidance is disallowed.",
                re.compile(
                    r"\b(how to|help me|show me|steps|code|script|make|build|create|"
                    r"install|bypass)\b"
                    r".{0,80}\b(persistence|persist|evasion|stealth|antivirus|edr|defender)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "persistence_or_evasion",
                "Persistence, evasion, stealth, and security-tool bypass guidance is disallowed.",
                re.compile(
                    r"\b(persistence|persist|evasion|stealth)\b.{0,80}"
                    r"\b(bypass|antivirus|edr|defender)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "unauthorized_access",
                "Unauthorized access and real account takeover requests are disallowed.",
                re.compile(
                    r"\b(hack|breach|break into|take over|exploit)\b.{0,80}"
                    r"\b(gmail|instagram|facebook|bank|paypal|company|school|account|"
                    r"real website|production)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "access_control_bypass",
                "Bypassing authentication, 2FA, paywalls, or access controls is disallowed.",
                re.compile(
                    r"\b(bypass|crack|brute\s?force|break)\b.{0,80}"
                    r"\b(login|password|2fa|mfa|authentication|paywall|access controls?)\b",
                    re.IGNORECASE,
                ),
            ),
            SafetyRule(
                "unauthorized_intent",
                "Requests framed as unauthorized or without permission are disallowed.",
                re.compile(
                    r"\b(without permission|unauthori[sz]ed|not authorized)\b",
                    re.IGNORECASE,
                ),
            ),
        ]
        self._ip_pattern = re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
        )
        self._scan_words = re.compile(r"\b(nmap|masscan|scan|enumerate|port scan)\b", re.IGNORECASE)

    def check(self, text: str) -> SafetyResult:
        normalized = text.strip()
        if not normalized:
            return SafetyResult(allowed=True)

        matched_categories: list[str] = []
        matched_reasons: list[str] = []
        for rule in self._rules:
            if rule.pattern.search(normalized):
                matched_categories.append(rule.category)
                matched_reasons.append(rule.reason)

        if self._looks_like_public_ip_scanning(normalized):
            matched_categories.append("public_ip_scanning")
            matched_reasons.append(
                "Scanning or enumerating public IPs is outside the bot's safe CTF scope."
            )

        if matched_categories:
            return SafetyResult(
                allowed=False,
                categories=tuple(dict.fromkeys(matched_categories)),
                reason=" ".join(dict.fromkeys(matched_reasons)),
                message=REFUSAL_MESSAGE,
            )

        return SafetyResult(allowed=True)

    def _looks_like_public_ip_scanning(self, text: str) -> bool:
        if not self._scan_words.search(text):
            return False

        for match in self._ip_pattern.findall(text):
            try:
                ip = ipaddress.ip_address(match)
            except ValueError:
                continue
            if not (ip.is_private or ip.is_loopback or ip.is_link_local):
                return True
        return False
