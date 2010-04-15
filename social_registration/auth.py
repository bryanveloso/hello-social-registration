from facebook.djangofb import get_facebook_client

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from models import FacebookProfile, TwitterProfile


class Auth(object):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class FacebookBackend(Auth):
    def authenticate(self, request=None):
        facebook = get_facebook_client()
        facebook.check_session(request)
        if facebook.uid:
            try:
                facebook_profile = FacebookProfile.objects.get(uid=facebook.uid)
                return facebook_profile.user
            except FacebookProfile.DoesNotExist:
                return None
            except User.DoesNotExist:
                return None


class TwitterBackend(Auth):
    def authenticate(self, twitter_id=None):
        try:
            twitter_profile = TwitterProfile.objects.get(twitter_id=twitter_id)
            return twitter_profile.user
        except:
            return None

