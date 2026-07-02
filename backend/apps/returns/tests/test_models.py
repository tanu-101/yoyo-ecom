from __future__ import annotations

import pytest

from apps.returns.factories import ReturnItemFactory, ReturnRequestFactory
from apps.returns.models import ReturnItem, ReturnRequest

pytestmark = pytest.mark.django_db


class TestReturnRequest:
    def test_create_return(self):
        ret = ReturnRequestFactory()
        assert ReturnRequest.objects.count() == 1
        assert str(ret).startswith("RET-")


class TestReturnItem:
    def test_create_item(self):
        ReturnItemFactory()
        assert ReturnItem.objects.count() == 1
