from __future__ import annotations

from apps.accounts.models import User
from apps.support.models import Ticket


class TicketService:
    @staticmethod
    def create_ticket(*, user: User, subject: str, message: str) -> Ticket:
        return Ticket.objects.create(user=user, subject=subject, message=message)

    @staticmethod
    def resolve_ticket(ticket: Ticket) -> Ticket:
        ticket.is_resolved = True
        ticket.save(update_fields=["is_resolved", "updated_at"])
        return ticket
