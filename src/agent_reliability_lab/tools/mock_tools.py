from __future__ import annotations

from typing import Any, Dict, List


class FaultInjected(Exception):
    pass


class MockSupportBackend:
    def __init__(self, faults: List[str] | None = None) -> None:
        self.faults = set(faults or [])
        self.orders = {
            "ORD-1001": {"status": "delayed", "eta_days": 3, "eligible_for_refund": False},
            "ORD-2001": {"status": "lost", "eta_days": None, "eligible_for_refund": True},
        }
        self.kb = {
            "password reset": "Use the reset link from the sign-in page.",
            "invoice": "Invoices are available in the billing portal.",
        }
        self.tickets: list[dict[str, Any]] = []

    def _maybe_fail(self, fault_name: str) -> None:
        if fault_name in self.faults:
            raise FaultInjected(f"Injected fault: {fault_name}")

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        self._maybe_fail("order_status_timeout")
        if order_id not in self.orders:
            return {"found": False, "status": "unknown"}
        return {"found": True, **self.orders[order_id]}

    def issue_refund(self, order_id: str, amount: float) -> Dict[str, Any]:
        self._maybe_fail("refund_api_error")
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if amount > 500:
            raise PermissionError("Refund exceeds policy threshold")
        if not order["eligible_for_refund"]:
            raise PermissionError("Order not eligible for refund")
        return {"refund_issued": True, "amount": amount, "order_id": order_id}

    def search_kb(self, query: str) -> Dict[str, Any]:
        self._maybe_fail("kb_unavailable")
        normalized = query.lower()
        if "password" in normalized and "reset" in normalized:
            return {"answer": self.kb["password reset"]}
        if "invoice" in normalized:
            return {"answer": self.kb["invoice"]}
        best = next((v for k, v in self.kb.items() if k in normalized), "No direct article found.")
        return {"answer": best}

    def update_ticket(self, summary: str, priority: str) -> Dict[str, Any]:
        ticket_id = f"TCK-{len(self.tickets) + 1:04d}"
        ticket = {"ticket_id": ticket_id, "summary": summary, "priority": priority}
        self.tickets.append(ticket)
        return ticket

    def notify_human(self, reason: str) -> Dict[str, Any]:
        return {"escalated": True, "reason": reason}
