from django.db import transaction
from rest_framework import serializers

from orchestra.api.serializers import SetPasswordHyperlinkedSerializer, RelatedHyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Mailbox, Address


class RelatedDomainSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = Address.domain.field.related_model
        fields = ('url', 'id', 'name')


class RelatedAddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    domain = RelatedDomainSerializer()

    class Meta:
        model = Address
        fields = ('url', 'id', 'name', 'domain', 'forward')
#
#    def from_native(self, data, files=None):
#        queryset = self.opts.model.objects.filter(account=self.account)
#        return get_object_or_404(queryset, name=data['name'])


class MailboxSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    addresses = RelatedAddressSerializer(many=True, read_only=True)

    class Meta:
        model = Mailbox
        fields = (
            'url', 'id', 'name', 'password', 'filtering', 'custom_filtering', 'addresses', 'is_active'
        )
        postonly_fields = ('name', 'password')


class RelatedMailboxSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'id', 'name')


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    domain = RelatedDomainSerializer()
    mailboxes = RelatedMailboxSerializer(many=True, required=False)

    class Meta:
        model = Address
        fields = ('url', 'id', 'name', 'domain', 'mailboxes', 'forward')

    def validate(self, attrs):
        attrs = super(AddressSerializer, self).validate(attrs)
        mailboxes = attrs.get('mailboxes', [])
        forward = attrs.get('forward', '')
        if not mailboxes and not forward:
            raise serializers.ValidationError("A mailbox or forward address should be provided.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        mailboxes = validated_data.pop('mailboxes', [])
        obj = super().create(validated_data)
        obj.mailboxes.set(mailboxes)
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        mailboxes = validated_data.pop('mailboxes', [])
        instance.mailboxes.set(mailboxes)
        return super().update(instance, validated_data)
