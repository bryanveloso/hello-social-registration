import httplib
import oauth2 as oauth

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from models import FacebookProfile, TwitterProfile
from utils import (CONSUMER_KEY, CONSUMER_SECRET, SERVER,
    get_unauthorized_request_token, get_authorization_url,
    exchange_request_token_for_access_token, is_authenticated)


CONSUMER = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
CONNECTION = httplib.HTTPSConnection(SERVER)

def facebook_authentication(request, template_name='accounts/facebook/login.html'):
    """
    Handles authentication with Facebook Connect.

    If the authenticated user does not yet have a ``User`` registered, they
    are redirected to the Facebook registration backend.

    """
    avatar = request.facebook.users.getInfo([request.facebook.uid], ['pic_square'])[0]

    if request.method == "POST":
        user = authenticate(request=request)
        # ``authenticate()`` worked and the user has a FacebookProfile
        # already, so let's fetch it and log them in.
        if user is not None:
            profile = FacebookProfile.objects.get(uid=request.facebook.uid)
            profile.avatar = avatar
            profile.save()
            if user.is_active:
                login(request, user)
                return redirect('site-home')
        # ``authenticate()`` didn't work, so we have an existing user trying
        # to connect, but they don't have a FacebookProfile yet, so let's
        # create one. We don't need to log them in though since they've
        # already done so.
        elif request.user.is_authenticated():
            user = request.user
            profile = FacebookProfile.objects.create(
                user=user,
                uid=request.facebook.uid,
                avatar=avatar
            )
            return redirect('edit-profile')
        # ``authenticate()`` didn't work, and the user is new, so let's send
        # them to registration to set a username and password.
        elif request.facebook.uid:
            return redirect('facebook-setup')

    return render_to_response(template_name, {}, context_instance=RequestContext(request))


def facebook_logout(request, login_url=None):
    """
    Logs a user out of Facebook and Django's authentication system.

    """
    if not login_url:
	    login_url = settings.LOGIN_URL
    logout(request, login_url)
    if getattr(request, 'facebook', False):
        request.facebook.session_key = None
        request.facebook.uid = None
    return redirect('site-home')


def twitter_authorization(request):
    """
    Handles the preliminary authorization steps between the site and Twitter's
    OAuth platform. A request token is sent and validated to recieve an
    authorization URL which the user is then redirected to.

    """
    token = get_unauthorized_request_token(CONSUMER)
    authorization_url = get_authorization_url(CONSUMER, token)
    request.session['unauthed_token'] = token.to_string()
    return redirect(authorization_url)


def twitter_unauthorization(request, login_url=None):
    """
    Unauthorizes a Twitter user's account and logs them out of Django's
    authentication system.

    """
    if not login_url:
	    login_url = settings.LOGIN_URL
    logout(request, login_url)
    request.session.clear()
    return redirect('site-home')


def twitter_callback(request):
    """
    Handles the user after authentication with Twitter's OAuth platform. If
    nothing has gone wrong, the user is once again sent to the primary login
    view to either finish setting up or to be logged in.

    """
    unauthed_token = request.session.get('unauthed_token', None)
    if not unauthed_token:
        return HttpResponse('No un-authed token cookie.')
    token = oauth.Token.from_string(unauthed_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return HttpResponse('Something went wrong! The tokens do not match.')
    access_token = exchange_request_token_for_access_token(CONSUMER, CONNECTION, token)
    request.session['access_token'] = access_token.to_string()
    return redirect('twitter-login')


def twitter_login(request, template_name='twitter/login.html'):
    """
    Handles authentication with Twitter's OAuth authentication platform.

    If the authenticated user does not yet have a ``User`` registered, they
    are redirected to the Twitter registration backend.

    """
    access_token = request.session.get('access_token', None)
    if not access_token:
        return redirect('twitter-authorization')
    token = oauth.Token.from_string(access_token)

    # Let's see if Twitter likes this token.
    auth = is_authenticated(CONSUMER, CONNECTION, token)
    if auth:
        # They like the token, so let's authenticate against it.
        user = authenticate(twitter_id=auth['id'])
        # ``authenticate()`` worked and the user has a TwitterProfile already,
        # so let's fetch it and log them in.
        if user is not None:
            profile = TwitterProfile.objects.get(twitter_id=auth['id'])
            profile.access_token = request.session.get('access_token', None) or profile.access_token
            profile.avatar = auth['profile_image_url']
            profile.save()
            if user.is_active:
                login(request, user)
            return redirect('site-home')
        # ``authenticate()`` didn't work, so we have an existing user trying
        # to connect, but they don't have a TwitterProfile yet, so let's
        # create one. We don't need to log them in though since they've
        # already done so.
        elif request.user.is_authenticated():
            user = request.user
            profile = TwitterProfile.objects.create(
                user=user,
                twitter_id=auth['id'],
                access_token=request.session.get('access_token', None),
                avatar=auth['profile_image_url']
            )
            return redirect('edit-profile')
        # ``authenticate()`` didn't work, and the user is new, so let's send
        # them to registration to set a username and password.
        else:
            request.session['twitter_id'] = auth['id']
            return redirect('twitter-setup')
    else:
        return HttpResponse('You are not authorized.')

    return render_to_response(template_name, {}, context_instance=RequestContext(request))

