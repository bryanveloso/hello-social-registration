from django.conf import settings
from django.contrib.auth.models import User

from registration import signals
from registration.forms import UserForm
from social_registration.models import TwitterProfile


class TwitterBackend(object):
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
        username, email = kwargs['username'], kwargs['email']
        new_user = User.objects.create_user(username, email)
        new_user.password = User.objects.set_unusable_password()
        new_user.save()

        new_twitter_profile = TwitterProfile(
            user=new_user,
            twitter_id=request.session.get('twitter_id', None),
        )
        new_twitter_profile.access_token = request.session.get('access_token', None) or new_twitter_profile.access_token
        new_twitter_profile.save()

        signals.user_registered.send(sender=self.__class__, user=new_user, request=request)
        return new_user

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
        return ('twitter-registration-complete', (), {})

