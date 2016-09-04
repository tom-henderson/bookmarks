from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import RedirectView


class LoginRequiredMixin(object):
    """
    Returns a 404 Unauthorised if the user is not logged in.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class SuperUserLoginRequiredMixin(object):
    """
    Returns 404 Unauthorised if the user is not a super user.
    """
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return super(SuperUserLoginRequiredMixin, self).dispatch(*args, **kwargs)
        return HttpResponse('Unauthorized', status=401)


class StaffLoginRequiredMixin(object):
    """
    Returns 404 Unauthorised if the user is not staff.
    """
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(StaffLoginRequiredMixin, self).dispatch(*args, **kwargs)
        return HttpResponse('Unauthorized', status=401)


class GenericLogOutView(RedirectView):
    """
    Provides users the ability to log out.
    Override url when subclassing.
    """
    url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(GenericLogOutView, self).get(request, *args, **kwargs)
