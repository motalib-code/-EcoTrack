"""
ElectionAssistant.py

Improved, rule-based conversational election assistant for India.

Highlights:
- Session-based context memory
- Intent detection without paid LLM APIs
- Guided conversational flows:
  1) Eligibility checker
  2) Voter registration steps
  3) State election timelines
  4) Voting-day checklist
- Response variation for a natural chat feel
- Optional typing simulation metadata for UI clients

This module is framework-agnostic and can be used from CLI, FastAPI, Flask,
or any frontend via a simple process_message() call.
"""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


# -----------------------------
# Core data models
# -----------------------------
@dataclass
class Progress:
    current: int
    total: int
    label: str


@dataclass
class AssistantResponse:
    messages: List[str]
    quick_replies: Optional[List[str]] = None
    progress: Optional[Progress] = None
    typing_delay_ms: int = 0


@dataclass
class UserSession:
    session_id: str
    current_flow: Optional[str] = None
    current_step: int = 0
    age: Optional[int] = None
    is_indian_citizen: Optional[bool] = None
    is_eligible: Optional[bool] = None
    state: Optional[str] = None
    history: List[str] = field(default_factory=list)


# -----------------------------
# Assistant implementation
# -----------------------------
class ElectionAssistant:
    def __init__(self, simulate_typing: bool = True) -> None:
        self.simulate_typing = simulate_typing
        self.sessions: Dict[str, UserSession] = {}

        self.main_menu = [
            "Check eligibility",
            "Register to vote",
            "Election timeline",
            "Voting day steps",
        ]

        self.intent_keywords = {
            "greeting": ["hi", "hello", "hey", "namaste"],
            "help": ["help", "menu", "options", "what can you do"],
            "eligibility": ["eligibility", "eligible", "can i vote", "age"],
            "registration": ["register", "registration", "form 6", "new voter"],
            "timeline": ["timeline", "date", "election date", "result"],
            "voting_day": ["voting day", "polling", "booth", "evm", "voting steps"],
        }

        self.indian_states = {
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
            "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand",
            "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur",
            "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
            "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura",
            "uttar pradesh", "uttarakhand", "west bengal", "delhi", "jammu and kashmir",
        }

        self.registration_steps = [
            "Visit NVSP (https://www.nvsp.in) or use the Voter Helpline app.",
            "Select Form 6: new voter registration.",
            "Fill personal details: name, DOB, and address.",
            "Upload recent passport photo.",
            "Upload age proof (birth certificate, class 10 certificate, passport, etc.).",
            "Upload address proof (Aadhaar, utility bill, bank passbook, etc.).",
            "Review entries carefully and submit.",
            "Save your reference/application ID.",
            "Track status in NVSP or Voter Helpline app.",
            "After approval, download your e-EPIC.",
        ]

        self.voting_day_steps = [
            "Check your name in electoral roll before polling day.",
            "Find your polling booth details from official slip/portal.",
            "Carry a valid photo ID.",
            "Reach booth within polling hours.",
            "Get verification and indelible ink marking.",
            "Use EVM to cast vote for your chosen candidate.",
            "Verify VVPAT display before leaving.",
            "Your vote is complete.",
        ]

        self.timelines = {
            "maharashtra": (date(2026, 9, 15), date(2026, 10, 20), date(2026, 10, 25), "State Assembly Elections"),
            "delhi": (date(2026, 11, 1), date(2026, 12, 5), date(2026, 12, 8), "Municipal Elections"),
            "karnataka": (date(2026, 8, 20), date(2026, 9, 25), date(2026, 9, 28), "Local Body Elections"),
            "tamil nadu": (date(2026, 10, 10), date(2026, 11, 15), date(2026, 11, 18), "Urban Local Body Elections"),
            "uttar pradesh": (date(2026, 7, 15), date(2026, 8, 20), date(2026, 8, 25), "Panchayat Elections"),
            "kerala": (date(2026, 9, 1), date(2026, 10, 10), date(2026, 10, 13), "Local Self Government Elections"),
            "odisha": (date(2026, 9, 5), date(2026, 10, 8), date(2026, 10, 11), "Local Governance Elections"),
        }

        self.variations = {
            "greeting": [
                "Hello. I am your Election Assistant for India.",
                "Namaste. I can guide you through voting and registration.",
                "Welcome. I can help with eligibility, registration, timelines, and voting-day steps.",
            ],
            "fallback": [
                "I did not fully understand. Choose one of the core options below.",
                "Let me help by routing you to a supported topic.",
                "I can guide you better if you pick one of the main options.",
            ],
            "eligible_yes": [
                "Good news. You are eligible to vote.",
                "Great. You meet the eligibility requirements.",
                "You are eligible. Your vote matters.",
            ],
            "eligible_no": [
                "You are not eligible yet based on current details.",
                "Right now, eligibility requirements are not fully met.",
                "You are currently ineligible, but I can guide your next steps.",
            ],
        }

    # -------------------------
    # Public entrypoint
    # -------------------------
    def process_message(self, session_id: str, message: str) -> AssistantResponse:
        session = self.sessions.get(session_id)
        if session is None:
            session = UserSession(session_id=session_id)
            self.sessions[session_id] = session

        clean = self._normalize(message)
        session.history.append(message)

        # Allow menu/help interrupt from any flow.
        if self._detect_intent(clean) == "help":
            self._reset_flow(session)
            return self._response(["Here is what I can help with:"], self.main_menu)

        # Continue active flow if exists.
        if session.current_flow:
            return self._continue_flow(session, clean)

        # Start new flow by intent.
        intent = self._detect_intent(clean)
        if intent == "greeting":
            return self._response([random.choice(self.variations["greeting"]), "What would you like to do?"], self.main_menu)
        if intent == "eligibility":
            return self._start_eligibility(session)
        if intent == "registration":
            return self._start_registration(session)
        if intent == "timeline":
            return self._start_timeline(session)
        if intent == "voting_day":
            return self._start_voting_day(session)
        if intent == "help":
            return self._response(["Here is what I can help with:"], self.main_menu)

        # Button-like direct commands.
        if clean == "check eligibility":
            return self._start_eligibility(session)
        if clean == "register to vote":
            return self._start_registration(session)
        if clean == "election timeline":
            return self._start_timeline(session)
        if clean == "voting day steps":
            return self._start_voting_day(session)

        return self._response([random.choice(self.variations["fallback"])], self.main_menu)

    # -------------------------
    # Intent and helper methods
    # -------------------------
    def _normalize(self, text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    def _detect_intent(self, text: str) -> str:
        for intent, keywords in self.intent_keywords.items():
            if any(k in text for k in keywords):
                return intent
        return "unknown"

    def _response(self, messages: List[str], quick_replies: Optional[List[str]] = None, progress: Optional[Progress] = None) -> AssistantResponse:
        joined_len = sum(len(m) for m in messages)
        delay_ms = min(1400, max(200, int(joined_len * 7))) if self.simulate_typing else 0
        return AssistantResponse(messages=messages, quick_replies=quick_replies, progress=progress, typing_delay_ms=delay_ms)

    def _reset_flow(self, session: UserSession) -> None:
        session.current_flow = None
        session.current_step = 0

    def _continue_flow(self, session: UserSession, text: str) -> AssistantResponse:
        if session.current_flow == "eligibility":
            return self._continue_eligibility(session, text)
        if session.current_flow == "registration":
            return self._continue_step_flow(session, text, "registration", self.registration_steps, "Voter Registration")
        if session.current_flow == "voting_day":
            return self._continue_step_flow(session, text, "voting_day", self.voting_day_steps, "Voting Day Guide")
        if session.current_flow == "timeline":
            return self._continue_timeline(session, text)

        self._reset_flow(session)
        return self._response(["Flow reset. Please choose an option."], self.main_menu)

    # -------------------------
    # Eligibility flow
    # -------------------------
    def _start_eligibility(self, session: UserSession) -> AssistantResponse:
        session.current_flow = "eligibility"
        session.current_step = 0
        session.age = None
        session.is_indian_citizen = None
        session.is_eligible = None
        return self._response(
            ["Let us check your voting eligibility.", "What is your age?"],
            progress=Progress(current=1, total=3, label="Eligibility Check"),
        )

    def _continue_eligibility(self, session: UserSession, text: str) -> AssistantResponse:
        if session.current_step == 0:
            if not text.isdigit():
                return self._response(["Please enter age as a number."], progress=Progress(1, 3, "Eligibility Check"))
            age = int(text)
            if age < 1 or age > 150:
                return self._response(["Please provide a realistic age between 1 and 150."], progress=Progress(1, 3, "Eligibility Check"))

            session.age = age
            session.current_step = 1
            return self._response(["Are you an Indian citizen? (yes/no)"], ["Yes", "No"], Progress(2, 3, "Eligibility Check"))

        if session.current_step == 1:
            yes = {"yes", "y", "haan", "ha", "true"}
            no = {"no", "n", "nahi", "false"}
            if text not in yes and text not in no:
                return self._response(["Please answer with yes or no."], ["Yes", "No"], Progress(2, 3, "Eligibility Check"))

            session.is_indian_citizen = text in yes
            session.is_eligible = bool(session.age and session.age >= 18 and session.is_indian_citizen)
            self._reset_flow(session)

            if session.is_eligible:
                return self._response(
                    [
                        random.choice(self.variations["eligible_yes"]),
                        f"Reason: age={session.age} and citizenship=Indian.",
                        "Would you like registration guidance next?",
                    ],
                    ["Register to vote", "Election timeline", "Main menu"],
                    Progress(3, 3, "Eligibility Check"),
                )

            reasons = []
            if session.age is not None and session.age < 18:
                reasons.append(f"minimum age is 18 (current: {session.age})")
            if session.is_indian_citizen is False:
                reasons.append("only Indian citizens can vote in Indian elections")

            return self._response(
                [
                    random.choice(self.variations["eligible_no"]),
                    "Reason: " + "; ".join(reasons),
                    "You can still explore registration and election timeline information.",
                ],
                self.main_menu,
                Progress(3, 3, "Eligibility Check"),
            )

        self._reset_flow(session)
        return self._response(["Eligibility flow reset."], self.main_menu)

    # -------------------------
    # Step flow (registration/voting day)
    # -------------------------
    def _start_registration(self, session: UserSession) -> AssistantResponse:
        session.current_flow = "registration"
        session.current_step = 0
        return self._response(
            [
                "Starting voter registration guide.",
                f"Step 1/{len(self.registration_steps)}: {self.registration_steps[0]}",
            ],
            ["Next", "Show all", "Main menu"],
            Progress(1, len(self.registration_steps), "Voter Registration"),
        )

    def _start_voting_day(self, session: UserSession) -> AssistantResponse:
        session.current_flow = "voting_day"
        session.current_step = 0
        return self._response(
            [
                "Starting voting-day guide.",
                f"Step 1/{len(self.voting_day_steps)}: {self.voting_day_steps[0]}",
            ],
            ["Next", "Show all", "Main menu"],
            Progress(1, len(self.voting_day_steps), "Voting Day Guide"),
        )

    def _continue_step_flow(
        self,
        session: UserSession,
        text: str,
        flow_name: str,
        steps: List[str],
        label: str,
    ) -> AssistantResponse:
        if text in {"main menu", "menu", "back"}:
            self._reset_flow(session)
            return self._response(["Returning to main menu."], self.main_menu)

        if text in {"show all", "all", "all steps"}:
            self._reset_flow(session)
            all_steps = [f"Step {i + 1}. {s}" for i, s in enumerate(steps)]
            return self._response(["\n".join(all_steps), "Guide complete."], self.main_menu)

        if text not in {"next", "done", "ok", "continue", "next step"}:
            return self._response(["Use Next to continue, Show all to view full guide, or Main menu."], ["Next", "Show all", "Main menu"], Progress(session.current_step + 1, len(steps), label))

        next_step = session.current_step + 1
        if next_step >= len(steps):
            self._reset_flow(session)
            return self._response([f"{label} completed.", "You are all set."], self.main_menu)

        session.current_step = next_step
        is_last = next_step == len(steps) - 1
        replies = ["Done", "Main menu"] if is_last else ["Next", "Show all", "Main menu"]
        return self._response(
            [f"Step {next_step + 1}/{len(steps)}: {steps[next_step]}"],
            replies,
            Progress(next_step + 1, len(steps), label),
        )

    # -------------------------
    # Timeline flow
    # -------------------------
    def _start_timeline(self, session: UserSession) -> AssistantResponse:
        session.current_flow = "timeline"
        session.current_step = 0
        popular = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Odisha", "Uttar Pradesh"]
        return self._response(
            ["Which state timeline do you want? Type a state name."],
            popular + ["Main menu"],
        )

    def _continue_timeline(self, session: UserSession, text: str) -> AssistantResponse:
        if text in {"main menu", "menu", "back"}:
            self._reset_flow(session)
            return self._response(["Returning to main menu."], self.main_menu)

        # Exact state match.
        if text in self.indian_states:
            return self._timeline_answer(session, text)

        # Suggest partial match.
        matches = [s for s in sorted(self.indian_states) if text in s]
        if matches:
            return self._response([f"Did you mean: {matches[0].title()}?"], [matches[0].title(), "Main menu"])

        return self._response(["State not recognized. Please type a valid Indian state name."], ["Main menu"])

    def _timeline_answer(self, session: UserSession, state_key: str) -> AssistantResponse:
        self._reset_flow(session)
        session.state = state_key.title()

        if state_key not in self.timelines:
            return self._response([f"Timeline data for {session.state} is not available yet."], self.main_menu)

        reg_deadline, election_day, result_day, notes = self.timelines[state_key]
        msg = (
            f"Election timeline for {session.state}\n"
            f"- Registration deadline: {reg_deadline.strftime('%d %b %Y')}\n"
            f"- Election date: {election_day.strftime('%d %b %Y')}\n"
            f"- Result date: {result_day.strftime('%d %b %Y')}\n"
            f"- Notes: {notes}"
        )
        return self._response([msg], self.main_menu)


# -----------------------------
# Optional CLI demo
# -----------------------------
def _demo() -> None:
    assistant = ElectionAssistant(simulate_typing=False)
    session_id = "cli-demo"
    print("Election Assistant CLI demo. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        response = assistant.process_message(session_id, user_input)
        if response.typing_delay_ms:
            time.sleep(response.typing_delay_ms / 1000.0)
        for line in response.messages:
            print(f"Assistant: {line}")
        if response.quick_replies:
            print("Quick replies:", " | ".join(response.quick_replies))
        if response.progress:
            print(f"Progress: {response.progress.current}/{response.progress.total} [{response.progress.label}]")
        print("-" * 60)


if __name__ == "__main__":
    _demo()
