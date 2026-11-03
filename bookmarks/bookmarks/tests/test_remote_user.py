import importlib
import os
from unittest import mock

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from bookmarks.remote_user import header_to_meta_key

REMOTE_MIDDLEWARE = 'bookmarks.remote_user.RemoteUserMiddleware'
REMOTE_BACKEND = 'bookmarks.remote_user.RemoteUserBackend'
MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'
AUTH_MIDDLEWARE = 'django.contrib.auth.middleware.AuthenticationMiddleware'


def _enabled_middleware():
    middleware = list(settings.MIDDLEWARE)
    middleware.insert(middleware.index(AUTH_MIDDLEWARE) + 1, REMOTE_MIDDLEWARE)
    return middleware


def remote_user_enabled(**kwargs):
    """override_settings with the remote user middleware/backend installed."""
    options = {
        'MIDDLEWARE': _enabled_middleware(),
        'AUTHENTICATION_BACKENDS': [REMOTE_BACKEND, MODEL_BACKEND],
        'REMOTE_USER_HEADER': 'Remote-User',
        'REMOTE_USER_FIELD': 'username',
        'REMOTE_USER_CREATE_UNKNOWN': False,
        'REMOTE_USER_GROUPS_HEADER': '',
        'REMOTE_USER_ADMIN_GROUPS': [],
    }
    options.update(kwargs)
    return override_settings(**options)


def _reload_base_settings(env):
    import config.settings.base as base
    keys = [k for k in os.environ if k.startswith('REMOTE_USER_')]
    clean_env = {k: v for k, v in os.environ.items() if k not in keys}
    clean_env.update(env)
    with mock.patch.dict(os.environ, clean_env, clear=True):
        return importlib.reload(base)


class RemoteUserSettingsTests(SimpleTestCase):
    def tearDown(self):
        # Restore the module to its state for the real environment.
        import config.settings.base as base
        importlib.reload(base)

    def test_header_to_meta_key(self):
        self.assertEqual(header_to_meta_key('Remote-User'), 'HTTP_REMOTE_USER')
        self.assertEqual(header_to_meta_key('Remote-Groups'), 'HTTP_REMOTE_GROUPS')

    def test_disabled_by_default(self):
        base = _reload_base_settings({})
        self.assertEqual(base.REMOTE_USER_HEADER, '')
        self.assertNotIn(REMOTE_MIDDLEWARE, base.MIDDLEWARE)
        self.assertEqual(tuple(base.AUTHENTICATION_BACKENDS), (MODEL_BACKEND,))
        self.assertEqual(base.REMOTE_USER_FIELD, 'username')
        self.assertFalse(base.REMOTE_USER_CREATE_UNKNOWN)
        self.assertEqual(base.REMOTE_USER_ADMIN_GROUPS, [])

    def test_enabled_adds_middleware_and_backend(self):
        base = _reload_base_settings({
            'REMOTE_USER_HEADER': 'Remote-User',
            'REMOTE_USER_FIELD': 'Email',
            'REMOTE_USER_CREATE_UNKNOWN': 'true',
            'REMOTE_USER_GROUPS_HEADER': 'Remote-Groups',
            'REMOTE_USER_ADMIN_GROUPS': 'admins, ops ,',
        })
        middleware = list(base.MIDDLEWARE)
        self.assertEqual(
            middleware.index(REMOTE_MIDDLEWARE),
            middleware.index(AUTH_MIDDLEWARE) + 1,
        )
        self.assertEqual(
            list(base.AUTHENTICATION_BACKENDS), [REMOTE_BACKEND, MODEL_BACKEND]
        )
        self.assertEqual(base.REMOTE_USER_FIELD, 'email')
        self.assertTrue(base.REMOTE_USER_CREATE_UNKNOWN)
        self.assertEqual(base.REMOTE_USER_ADMIN_GROUPS, ['admins', 'ops'])

    def test_invalid_field_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            _reload_base_settings({'REMOTE_USER_FIELD': 'first_name'})

    def test_test_settings_have_feature_disabled(self):
        self.assertNotIn(REMOTE_MIDDLEWARE, settings.MIDDLEWARE)
        self.assertNotIn(REMOTE_BACKEND, settings.AUTHENTICATION_BACKENDS)


class RemoteUserDisabledTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tom', 'tom@example.com', 'password')

    def test_header_ignored_when_disabled(self):
        response = self.client.get(reverse('index'), HTTP_REMOTE_USER='tom')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotIn(SESSION_KEY, self.client.session)


class RemoteUserAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tom', 'Tom@Example.com', 'password')

    def get(self, path=None, **headers):
        return self.client.get(path or reverse('index'), **headers)

    @remote_user_enabled()
    def test_login_by_username(self):
        response = self.get(HTTP_REMOTE_USER='tom')
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(self.client.session[SESSION_KEY], str(self.user.pk))

    @remote_user_enabled()
    def test_session_persists_without_header(self):
        self.get(HTTP_REMOTE_USER='tom')
        response = self.get()
        self.assertEqual(response.wsgi_request.user, self.user)

    @remote_user_enabled()
    def test_different_header_user_replaces_session(self):
        other = User.objects.create_user('alice', 'alice@example.com')
        self.get(HTTP_REMOTE_USER='tom')
        response = self.get(HTTP_REMOTE_USER='alice')
        self.assertEqual(response.wsgi_request.user, other)

    @remote_user_enabled(REMOTE_USER_FIELD='email')
    def test_login_by_email_case_insensitive(self):
        response = self.get(HTTP_REMOTE_USER='tom@EXAMPLE.com')
        self.assertEqual(response.wsgi_request.user, self.user)

    @remote_user_enabled(REMOTE_USER_FIELD='email')
    def test_email_login_session_is_stable(self):
        self.get(HTTP_REMOTE_USER='tom@example.com')
        session_key = self.client.session.session_key
        response = self.get(HTTP_REMOTE_USER='tom@example.com')
        self.assertEqual(response.wsgi_request.user, self.user)
        # Not logged out and back in on every request.
        self.assertEqual(self.client.session.session_key, session_key)

    @remote_user_enabled(REMOTE_USER_FIELD='email')
    def test_ambiguous_email_refused(self):
        User.objects.create_user('tom2', 'tom@example.com')
        with self.assertLogs('bookmarks.remote_user', level='WARNING'):
            response = self.get(HTTP_REMOTE_USER='tom@example.com')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    @remote_user_enabled()
    def test_unknown_user_rejected_when_create_disabled(self):
        response = self.get(HTTP_REMOTE_USER='stranger')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(User.objects.filter(username='stranger').exists())

    @remote_user_enabled(REMOTE_USER_CREATE_UNKNOWN=True)
    def test_unknown_user_created_with_email(self):
        response = self.get(
            HTTP_REMOTE_USER='newbie', HTTP_REMOTE_EMAIL='newbie@example.com'
        )
        user = User.objects.get(username='newbie')
        self.assertEqual(response.wsgi_request.user, user)
        self.assertEqual(user.email, 'newbie@example.com')
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    @remote_user_enabled(REMOTE_USER_CREATE_UNKNOWN=True, REMOTE_USER_FIELD='email')
    def test_unknown_user_created_by_email(self):
        response = self.get(HTTP_REMOTE_USER='new@example.com')
        user = User.objects.get(email='new@example.com')
        self.assertEqual(user.username, 'new@example.com')
        self.assertEqual(response.wsgi_request.user, user)
        self.assertFalse(user.has_usable_password())

    @remote_user_enabled()
    def test_inactive_user_refused(self):
        self.user.is_active = False
        self.user.save()
        response = self.get(HTTP_REMOTE_USER='tom')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    @remote_user_enabled(
        REMOTE_USER_GROUPS_HEADER='Remote-Groups',
        REMOTE_USER_ADMIN_GROUPS=['admins'],
    )
    def test_admin_group_grants_staff_and_superuser(self):
        self.get(HTTP_REMOTE_USER='tom', HTTP_REMOTE_GROUPS='family, admins')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)
        response = self.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    @remote_user_enabled(
        REMOTE_USER_GROUPS_HEADER='Remote-Groups',
        REMOTE_USER_ADMIN_GROUPS=['admins'],
    )
    def test_admin_group_revoked_when_not_in_group(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.get(HTTP_REMOTE_USER='tom', HTTP_REMOTE_GROUPS='family')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @remote_user_enabled(REMOTE_USER_GROUPS_HEADER='Remote-Groups')
    def test_flags_untouched_without_admin_groups(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.get(HTTP_REMOTE_USER='tom', HTTP_REMOTE_GROUPS='family')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

    @remote_user_enabled(REMOTE_USER_ADMIN_GROUPS=['admins'])
    def test_flags_untouched_without_groups_header(self):
        self.get(HTTP_REMOTE_USER='tom', HTTP_REMOTE_GROUPS='admins')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @remote_user_enabled()
    def test_password_login_still_works(self):
        response = self.client.post(reverse('log_in'), {
            'username': 'tom',
            'password': 'password',
        })
        self.assertEqual(response.status_code, 302)
        response = self.get()
        self.assertEqual(response.wsgi_request.user, self.user)

    @remote_user_enabled()
    def test_password_session_kept_when_header_names_same_user(self):
        self.client.post(reverse('log_in'), {'username': 'tom', 'password': 'password'})
        response = self.get(HTTP_REMOTE_USER='tom')
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(
            self.client.session['_auth_user_backend'], MODEL_BACKEND
        )
