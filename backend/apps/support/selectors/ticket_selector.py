from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.support.models import Ticket


class TicketSelector:
    @staticmethod
    def get_user_tickets(user: User) -> QuerySet[Ticket]:
        return Ticket.objects.filter(user=user, deleted_at__isnull=True)

    @staticmethod
    def get_all_unresolved() -> QuerySet[Ticket]:
        return Ticket.objects.filter(is_resolved=False, deleted_at__isnull=True)
