from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as standard_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.generic import simple

from accounts.backends import get_backend
from accounts.forms import ExtendedAuthenticationForm


def prepare(request, backend, **kwargs):
    """
    Handles a redirection to the returned URL from the given backend for use
    before the user authenticates with an external service. For example, an
    OAuth service provider will require this step grant the application a
    "request token" needed to proceed further.

    """
    backend = get_backend(backend)
    return redirect(backend.prepare(request))


def authenticate(request, backend, **kwargs):
    """
    Handles a user returned from the given backend's authenticate() method.
    Depending on what is returned a user will either be logged in, "linked" or
    created.

    """
    backend = get_backend(backend)
    user = backend.authenticate(request)

    if user is not None:
        return backend.grant_user(request, user)
    elif request.user.is_authenticated():
        return backend.link_user(request, user)
    else:
        return backend.create_user(request, user)


@login_required
def deauthenticate(request, backend, **kwargs):
    """
    Handles a user wishing to deactivate a connection between an
    authentication backend and their database account.

    """
    backend = get_backend(backend)
    success = backend.deauthenticate(request)
    return redirect('edit-profile')


@never_cache
def login(request, template_name='accounts/login.html',
    redirect_field_name=REDIRECT_FIELD_NAME,
    authentication_form=ExtendedAuthenticationForm):
    """
    A copy of ``django.contrib.auth.views.login()`` that inherits an extended
    authentication form allowing the user to save their session. Its template
    contains all the different methods for authentication. However, if sent
    a POST, it will use Django's default account backend to log the user in.

    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            standard_login(request, form.get_user())
            messages.success(request, 'Welcome back! You have been logged in!')
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if form.cleaned_data['remember']:
                request.session[settings.PERSISTENT_SESSION_KEY] = True
            else:
                request.session.set_expiry(0)
            return redirect(redirect_to)
    else:
        form = authentication_form(request)
    request.session.set_test_cookie()

    return simple.direct_to_template(request,
        template = template_name,
        extra_context = {
            'form': form,
            redirect_field_name: redirect_to,
        }
    )


def logout_then_login(request, login_url=None):
    """
    A wrapper around ``django.contrib.auth.views.logout_then_login()`` that
    includes an additional call to flush the user's session upon logging out
    before redirecting to the login page.

    """
    from django.contrib.auth import logout_then_login

    if not login_url:
        login_url = settings.LOGIN_URL
    request.session.clear()
    messages.success(request, 'You have been logged out. You may log in again below.')
    return logout_then_login(request, login_url)


