from rest_framework import viewsets

from orchestra.api import router, SetPasswordApiMixin, LogApiMixin
from orchestra.contrib.accounts.api import AccountApiMixin

from .models import Address, Mailbox
from .serializers import AddressSerializer, MailboxSerializer, MailboxWritableSerializer


class AddressViewSet(LogApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = Address.objects.select_related('domain').prefetch_related('mailboxes').all()
    serializer_class = AddressSerializer
    filter_fields = ('domain', 'mailboxes__name')


class MailboxViewSet(LogApiMixin, SetPasswordApiMixin, AccountApiMixin, viewsets.ModelViewSet):
    queryset = Mailbox.objects.prefetch_related('addresses__domain').all()
    serializer_class = MailboxSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class

        return MailboxWritableSerializer


router.register(r'mailboxes', MailboxViewSet)
router.register(r'addresses', AddressViewSet)
