from django.conf import settings
from django.utils.translation import ugettext_lazy as _


ACCOUNTS_TYPES = getattr(settings, 'ACCOUNTS_TYPES', (
    ('INDIVIDUAL', _("Individual")),
    ('ASSOCIATION', _("Association")),
    ('CUSTOMER', _("Customer")),
    ('COMPANY', _("Company")),
    ('PUBLICBODY', _("Public body")),
))

ACCOUNTS_DEFAULT_TYPE = getattr(settings, 'ACCOUNTS_DEFAULT_TYPE', 'INDIVIDUAL')


ACCOUNTS_LANGUAGES = getattr(settings, 'ACCOUNTS_LANGUAGES', (
    ('en', _('English')),
))


ACCOUNTS_DEFAULT_LANGUAGE = getattr(settings, 'ACCOUNTS_DEFAULT_LANGUAGE', 'en')


ACCOUNTS_MAIN_PK = getattr(settings, 'ACCOUNTS_MAIN_PK', 1)


ACCOUNTS_HOME = getattr(settings, 'ACCOUNTS_HOME', '/home/%(username)s')


ACCOUNTS_FTP_LOG_PATH = getattr(settings, 'ACCOUNTS_FTP_LOG_PATH', '/var/log/vsftpd.log')


ACCOUNTS_DEFAULT_SHELL = getattr(settings, 'ACCOUNTS_DEFAULT_SHELL', '/bin/false')
