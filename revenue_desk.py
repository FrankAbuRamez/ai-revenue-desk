"""Safe, deterministic lead-intake core for the AI Revenue Desk demo."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


class IntakeError(ValueError):
    """Raised when required lead information is missing."""


class RevenueDesk:
    REQUIRED_FIELDS = ("name", "phone", "service", "problem", "zip_code", "preferred_time")
    URGENT_PHRASES = (
        "gas leak",
        "smell gas",
        "carbon monoxide",
        "sparks",
        "electrical fire",
        "burst pipe",
        "flooding",
        "no heat",
    )

    def __init__(self, business_name: str) -> None:
        self.business_name = business_name
        self._leads: list[dict] = []

    def intake(self, payload: dict) -> dict:
        cleaned = {key: str(payload.get(key, "")).strip() for key in self.REQUIRED_FIELDS}
        missing = [key for key, value in cleaned.items() if not value]
        if missing:
            raise IntakeError(f"Missing required fields: {', '.join(missing)}")

        problem_lower = cleaned["problem"].lower()
        urgent = any(phrase in problem_lower for phrase in self.URGENT_PHRASES)
        status = "human_escalation" if urgent else "ready_to_book"
        priority = "urgent" if urgent else "normal"

        if urgent:
            customer_message = (
                f"Thanks, {cleaned['name']}. I’m alerting a human dispatcher now. "
                "If there is immediate danger, leave the area and contact emergency services. "
                "I cannot diagnose the problem or promise an arrival time."
            )
        else:
            customer_message = (
                f"Thanks, {cleaned['name']}. I’ve captured your {cleaned['service']} request "
                f"for {cleaned['preferred_time']}. A human will confirm the appointment and pricing."
            )

        lead = {
            "id": f"lead_{uuid4().hex[:10]}",
            "received_at": datetime.now(UTC).isoformat(),
            **cleaned,
            "status": status,
            "priority": priority,
            "customer_message": customer_message,
            "automation": {
                "diagnosis_given": False,
                "binding_price_given": False,
                "arrival_time_promised": False,
                "human_review_required": urgent,
            },
        }
        self._leads.append(lead)
        return lead.copy()

    def leads(self) -> list[dict]:
        return [lead.copy() for lead in reversed(self._leads)]

    def summary(self) -> dict:
        return {
            "business_name": self.business_name,
            "total_leads": len(self._leads),
            "ready_to_book": sum(lead["status"] == "ready_to_book" for lead in self._leads),
            "urgent": sum(lead["priority"] == "urgent" for lead in self._leads),
            "human_escalations": sum(lead["status"] == "human_escalation" for lead in self._leads),
        }
