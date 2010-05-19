import json
import urllib
import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from registration import signals
from registration.forms import UserForm
from social_registration.backends.default import AccountBackend as DefaultBackend
from social_registration.models import Association


class AuthenticationBackend(ModelBackend):
    def authenticate(self, identifier):
        try:
            association = Association.objects.get(identifier=identifier, service='facebook')
            return association.user
        except (Association.DoesNotExist, User.DoesNotExist):
            return None


class AccountBackend(DefaultBackend):
    """
    An account backend providing methods for an authentication workflow using
    the Facebook Platform (OAuth 2.0).

    """
    def __init__(self, *args, **kwargs):
        # URLs
        self.access_token_url = 'https://graph.facebook.com/oauth/access_token'
        self.authorize_url = 'https://graph.facebook.com/oauth/authorize'
        self.graph_url = 'https://graph.facebook.com/me'

        # Instance Variables
        self.access_token = None
        self.parameters = {
            'client_id': settings.FACEBOOK_APPLICATION_ID,
            'scope': 'email,user_birthday,publish_stream'
        }
        self.profile = None
        self.service = 'facebook'
        super(AccountBackend, self).__init__(*args, **kwargs)

    def prepare(self, request, **kwargs):
        """
        Although Facebook Platform doesn't use three-legged OAuth process, the
        ``authenticate()`` method cannot return anything other than a user. So
        all the logic to grab an authentication code for use in the method is
        done here.

        """
        verification_code = request.GET.get('code', None)
        if verification_code is None:
            self.parameters['redirect_uri'] = request.build_absolute_uri(reverse('facebook-authentication'))
            return '%s?%s' % (self.authorize_url, urllib.urlencode(self.parameters))
        return reverse('facebook-authentication')

    def authenticate(self, request, **kwargs):
        """
        Handles authentication with Facebook Platform. If the authenticated
        user does not yet have a ``User`` registered, they are redirected to
        the Facebook registration backend.

        """
        self.parameters['client_secret'] = settings.FACEBOOK_SECRET_KEY
        self.parameters['code'] = request.GET.get('code')
        self.parameters['redirect_uri'] = request.build_absolute_uri(request.path)

        response = urlparse.parse_qs(urllib.urlopen('%s?%s' % (self.access_token_url, urllib.urlencode(self.parameters))).read())
        self.access_token = response['access_token'][-1]
        self.profile = json.load(urllib.urlopen('%s?%s' % (self.graph_url, urllib.urlencode({'access_token': self.access_token}))))
        return authenticate(identifier=self.profile['id'])

    def create_user(self, request, user, **kwargs):
        """
        ``authenticate()`` returned ``None``, so the user is new. Let's send
        them to registration to set a username and password.

        """
        request.session['facebook_access_token'] = self.access_token
        request.session['facebook_identifier'] = self.profile['id']
        request.session['facebook_profile'] = self.profile
        return redirect('facebook-setup')

    def link_user(self, request, user, **kwargs):
        """
        ``authenticate()`` worked, so we have an existing user trying to
        connect, but they don't have an Association yet, so let's create one.
        We don't need to log them in though since they've already done so.

        """
        association = Association.get_or_create(
            access_token=self.access_token,
            avatar=request.facebook.graph.get_connections(self.profile['id'], 'picture'),
            identifier=self.profile['id'],
            is_active=True,
            profile_url=self.profile['link'],
            service=self.service,
            user=request.user
        )
        association.save()
        messages.success(request, 'Your Facebook account has been linked with your Hello! Ranking account.')
        return redirect('edit-profile')

    def grant_user(self, request, user, **kwargs):
        """
        ``authenticate()`` worked and the user has an ``Association`` already,
        so let's fetch it and log them in.

        """
        association = Association.objects.get(user=user, service=self.service)
        association.access_token = self.access_token
        association.avatar = request.facebook.graph.get_connections(self.profile['id'], 'picture')
        association.profile_url = self.profile['link']
        association.save()
        if user.is_active:
            login(request, user)
            messages.success(request, 'Welcome back! You have been logged in!')
            return redirect('site-home')

    def deauthenticate(self, request, **kwargs):
        """
        Breaks the link between a user and a Facebook account they had
        previously authenticated with.

        """
        association = Association.objects.get(user=request.user, service=self.service)
        association.is_active = False
        return True


class RegistrationBackend(object):
    """
    A registration backend which uses Facebook Connect, following a simple
    workflow.

        1.  User authenticates with Facebook.
        2.  User is sent to a form, asking them for their username and email.
        3.  Account is marked as active only after the user completes the
            aforementioned form.

    Registration can be temporarily closed by adding the setting
    ``REGISTRATION_OPEN`` and setting it to ``False``. Omitting this setting,
    or setting it to ``True``, will be interpreted as meaning that
    registration is currently open and permitted.

    """
    def register(self, request, **kwargs):
        """
        Given a username and email, create a new user, an accompanying profile
        and a relation to the Facebook user they authenticated with.

        """
        # Let's alias some of these session variables.
        access_token = request.session['facebook_access_token']
        identifier = request.session['facebook_identifier']
        profile = request.session['facebook_profile']

        username, email = kwargs['username'], kwargs['email']
        user = User.objects.create_user(username, email)
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.set_unusable_password()
        user.save()

        association = Association(
            access_token=access_token,
            avatar=request.facebook.graph.get_connections(identifier, 'picture'),
            identifier=identifier,
            is_active=True,
            profile_url=profile['link'],
            service='facebook',
            user=user
        )
        association.save()
        signals.user_registered.send(sender=self.__class__, user=user, request=request)
        return user

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``FACEBOOK_REGISTRATION_OPEN``.
        This is determined as follows:

        *  If ``FACEBOOK_REGISTRATION_OPEN`` is not specified in settings, or
           is set to ``True``, registration is permitted.

        *  If ``FACEBOOK_REGISTRATION_OPEN`` is both specified and set to
           ``False``, registration is not permitted.

        """
        return getattr(settings, 'FACEBOOK_REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.

        """
        return UserForm

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after a successful
        user registration.

        """
        return ('login', (), {})


