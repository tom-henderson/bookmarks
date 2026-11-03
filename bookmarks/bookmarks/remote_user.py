"""Trusted proxy header ("remote user") authentication.

Opt-in: nothing in this module is used unless ``REMOTE_USER_HEADER`` is set,
in which case ``config.settings.base`` adds ``RemoteUserMiddleware`` to
``MIDDLEWARE`` and ``RemoteUserBackend`` to ``AUTHENTICATION_BACKENDS``.

The reverse proxy (e.g. Traefik forwardAuth + Tinyauth) authenticates the user
and passes their identity in a request header. Only enable this when the app
can be reached exclusively through a proxy that sets or strips that header on
every route, otherwise anyone can log in as anyone by sending the header.
"""
import logging

from django.conf import settings
from django.contrib.auth import backends, get_user_model, middleware
from django.db import IntegrityError, transaction

logger = logging.getLogger(__name__)

# Proxy header carrying the user's email, used to populate the email of users
# created when REMOTE_USER_FIELD is "username".
REMOTE_EMAIL_HEADER = 'Remote-Email'


def header_to_meta_key(header):
    """Convert an HTTP header name (``Remote-User``) to its ``request.META`` key."""
    return 'HTTP_' + header.upper().replace('-', '_')


def _get_header(request, header):
    if request is None or not header:
        return ''
    return request.META.get(header_to_meta_key(header), '').strip()


def _remote_user_field():
    return getattr(settings, 'REMOTE_USER_FIELD', 'username')


class RemoteUserMiddleware(middleware.PersistentRemoteUserMiddleware):
    """Log in the user named by the ``REMOTE_USER_HEADER`` request header.

    Persistent: the Django session survives on routes where the proxy does not
    send the header. If the header names a different user than the one logged
    in via this backend, that session is logged out and replaced.
    """

    @property
    def header(self):
        header = getattr(settings, 'REMOTE_USER_HEADER', '')
        if not header:
            # No META key can match this, so the middleware does nothing.
            return 'REMOTE_USER_HEADER_NOT_CONFIGURED'
        return header_to_meta_key(header)

    def _matches_current_user(self, username, request):
        # When matching on email the header value is not the username, so
        # Django's username comparison would log the user out and back in on
        # every request. Treat a matching email as "already logged in".
        if _remote_user_field() != 'email':
            return False
        email = getattr(request.user, 'email', '') or ''
        return bool(email) and email.lower() == username.strip().lower()

    def clean_username(self, username, request):
        if self._matches_current_user(username, request):
            return request.user.get_username()
        return super().clean_username(username, request)

    async def aclean_username(self, username, request):
        user = await request.auser()
        email = getattr(user, 'email', '') or ''
        if (
            _remote_user_field() == 'email'
            and email
            and email.lower() == username.strip().lower()
        ):
            return user.get_username()
        return await super().aclean_username(username, request)


class RemoteUserBackend(backends.RemoteUserBackend):
    """Authenticate users identified by a trusted proxy header.

    Matches the header value against ``REMOTE_USER_FIELD`` (``username`` or
    case-insensitive ``email``), optionally creates unknown users, and
    optionally syncs ``is_staff``/``is_superuser`` from a groups header.
    """

    @property
    def create_unknown_user(self):
        return getattr(settings, 'REMOTE_USER_CREATE_UNKNOWN', False)

    def clean_username(self, username):
        return username.strip()

    def authenticate(self, request, remote_user):
        if not remote_user:
            return None
        value = self.clean_username(remote_user)
        if not value:
            return None

        UserModel = get_user_model()
        field = _remote_user_field()
        if field == 'email':
            lookup = {'email__iexact': value}
        else:
            lookup = {UserModel.USERNAME_FIELD: value}

        matches = list(UserModel._default_manager.filter(**lookup)[:2])
        if len(matches) > 1:
            logger.warning(
                'Remote user login refused: multiple users match %s=%r',
                field, value,
            )
            return None

        created = False
        if matches:
            user = matches[0]
        elif self.create_unknown_user:
            user = self._create_user(request, UserModel, field, value)
            if user is None:
                return None
            created = True
        else:
            logger.info(
                'Remote user login refused: no user with %s=%r', field, value,
            )
            return None

        user = self.configure_user(request, user, created=created)
        return user if self.user_can_authenticate(user) else None

    def _create_user(self, request, UserModel, field, value):
        if field == 'email':
            username, email = value, value
        else:
            username, email = value, _get_header(request, REMOTE_EMAIL_HEADER)
        try:
            with transaction.atomic():
                # No password given, so create_user sets an unusable password.
                user = UserModel._default_manager.create_user(
                    **{UserModel.USERNAME_FIELD: username, 'email': email}
                )
        except IntegrityError:
            logger.warning(
                'Remote user login refused: could not create user %r '
                '(username already exists)', username,
            )
            return None
        logger.info('Created user %r from remote user header', username)
        return user

    async def aauthenticate(self, request, remote_user):
        from asgiref.sync import sync_to_async
        return await sync_to_async(self.authenticate)(request, remote_user)

    def configure_user(self, request, user, created=True):
        groups_header = getattr(settings, 'REMOTE_USER_GROUPS_HEADER', '')
        admin_groups = set(getattr(settings, 'REMOTE_USER_ADMIN_GROUPS', []))
        if not (groups_header and admin_groups):
            return user

        groups = {
            g.strip() for g in _get_header(request, groups_header).split(',')
            if g.strip()
        }
        is_admin = bool(groups & admin_groups)
        if user.is_staff != is_admin or user.is_superuser != is_admin:
            user.is_staff = is_admin
            user.is_superuser = is_admin
            user.save(update_fields=['is_staff', 'is_superuser'])
            logger.info(
                'Set is_staff/is_superuser=%s for %r from remote groups',
                is_admin, user.get_username(),
            )
        return user
