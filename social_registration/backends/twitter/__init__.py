import oauth2 as oauth
import twitter
import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.shortcuts import redirect

from registration import signals
from registration.forms import UserForm
from social_registration.backends.default import AccountBackend as DefaultBackend
from social_registration.models import Association


class AuthenticationBackend(ModelBackend):
    def authenticate(self, identifier=None):
        try:
            association = Association.objects.get(identifier=identifier, service='twitter')
            return association.user
        except (Association.DoesNotExist, User.DoesNotExist):
            return None


class AccountBackend(DefaultBackend):
    """
    An account backend providing methods for an authentication workflow using
    Twitter (OAuth 1.0).

    """
    def __init__(self, *args, **kwargs):
        # URLs
        self.access_token_url = 'https://api.twitter.com/oauth/access_token'
        self.authenticate_url = 'http://api.twitter.com/oauth/authenticate'
        self.request_token_url = 'https://api.twitter.com/oauth/request_token'
        self.profile_url = 'http://twitter.com/%s'

        # Instance Variables
        self.access_token = None
        self.consumer = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
        self.identifier = None
        self.service = 'twitter'
        super(AccountBackend, self).__init__(*args, **kwargs)

    def prepare(self, request, **kwargs):
        """
        Handles the preliminary steps between the site and Twitter's OAuth
        platform. A request token is sent and validated to receive an
        authorization URL which the user is then redirected to.

        """
        client = oauth.Client(self.consumer)
        response, content = client.request(self.request_token_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response from Twitter.')
        request.session['request_token'] = dict(urlparse.parse_qsl(content))
        url = '%s?oauth_token=%s' % (self.authenticate_url, request.session['request_token']['oauth_token'])
        return url

    def authenticate(self, request, **kwargs):
        """
        Handles authentication with Twitter's OAuth authentication platform.
        If the authenticated user does not yet have a ``User`` registered,
        they are redirected to the Twitter registration backend.

        This is what you'll get back from Twitter. Note that it includes the
        user's user_id and screen_name.

        {
            'oauth_token_secret': 'IcJXPiJh8be3BjDWW50uCY31chyhsMHEhqJVsphC3M',
            'user_id': '120889797',
            'oauth_token': '120889797-H5zNnM3qE0iFoTTpNEHIz3noL9FKzXiOxwtnyVOD',
            'screen_name': 'heyismysiteup'
        }

        """
        token = oauth.Token(
            request.session['request_token']['oauth_token'],
            request.session['request_token']['oauth_token_secret']
        )
        client = oauth.Client(self.consumer, token)
        response, content = client.request(self.access_token_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response from Twitter.')
            return (False, None)
        self.access_token = dict(urlparse.parse_qsl(content))
        self.identifier = self.access_token['user_id']
        return authenticate(identifier=self.identifier)

    def create_user(self, request, user, **kwargs):
        """
        ``authenticate()`` returned ``None``, so the user is new. Let's send
        them to registration to set a username and password.

        """
        request.session['twitter_profile'] = twitter.Twitter().users.show(id=self.identifier)
        request.session['twitter_identifier'] = self.identifier
        return redirect('twitter-setup')

    def link_user(self, request, user, **kwargs):
        """
        ``authenticate()`` worked, so we have an existing user trying to
        connect, but they don't have an Association yet, so let's create one.
        We don't need to log them in though since they've already done so.

        """
        profile = twitter.Twitter().users.show(id=self.identifier)
        association = Association.get_or_create(
            access_token={
                'oauth_token': self.access_token['oauth_token'],
                'oauth_token_secret': self.access_token['oauth_token_secret']
            },
            avatar=profile['profile_image_url'],
            identifier=self.identifier,
            is_active=True,
            profile_url=self.profile_url % self.access_token['name'],
            service=self.service,
            user=user
        )
        association.save()
        messages.success(request, 'Your Twitter account has been linked with your Hello! Ranking account.')
        return redirect('edit-profile')

    def grant_user(self, request, user, **kwargs):
        """
        ``authenticate()`` worked and the user has an ``Association`` already,
        so let's fetch it and log them in.

        """
        try:
            twitter_profile = twitter.Twitter().users.show(id=self.access_token['user_id'])
            avatar = twitter_profile['profile_image_url']
        except:
            avatar = ''
        association = Association.objects.get(identifier=self.access_token['user_id'], service=self.service)
        association.access_token = {
            'oauth_token': self.access_token['oauth_token'],
            'oauth_token_secret': self.access_token['oauth_token_secret']
        }
        association.avatar = avatar
        association.save()
        if user.is_active:
            login(request, user)
            messages.success(request, 'Welcome back! You have been logged in!')
            return redirect('site-home')

    def deauthenticate(self, request, **kwargs):
        """
        Breaks the link between a user and a Twitter account they had
        previously authenticated with.

        """
        association = Association.objects.get(user=request.user, service=self.service)
        association.is_active = False
        return True


class RegistrationBackend(object):
    """
    A registration backend which uses Twitter, following a simple workflow.

        1.  User authenticates with Twitter.
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
        and a relation to the Twitter user they authenticated with.

        """
        # Let's alias some of these session variables.
        identifier = request.session['twitter_identifier']
        profile = request.session['twitter_profile']

        username, email = kwargs['username'], kwargs['email']
        user = User.objects.create_user(username, email)
        user.set_unusable_password()
        user.save()

        association = Association(
            access_token={
                'oauth_token': request.session['request_token']['oauth_token'],
                'oauth_token_secret': request.session['request_token']['oauth_token_secret']
            },
            avatar=profile['profile_image_url'],
            identifier=identifier,
            is_active=True,
            profile_url=self.profile_url % self.access_token['name'],
            service='twitter',
            user=user
        )
        association.save()
        signals.user_registered.send(sender=self.__class__, user=user, request=request)
        return user

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``TWITTER_REGISTRATION_OPEN``.
        This is determined as follows:

        *  If ``TWITTER_REGISTRATION_OPEN`` is not specified in settings, or
           is set to ``True``, registration is permitted.

        *  If ``TWITTER_REGISTRATION_OPEN`` is both specified and set to
           ``False``, registration is not permitted.

        """
        return getattr(settings, 'TWITTER_REGISTRATION_OPEN', True)

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


