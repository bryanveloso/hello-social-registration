import cgi
import oauth2 as oauth
import twitter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from models import FacebookProfile, TwitterProfile


# Twitter OAuth specific variables.
consumer = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
access_token_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'http://api.twitter.com/oauth/authenticate'
request_token_url = 'https://api.twitter.com/oauth/request_token'

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


def twitter_authentication(request):
    """
    Handles the preliminary authorization steps between the site and Twitter's
    OAuth platform. A request token is sent and validated to recieve an
    authorization URL which the user is then redirected to.

    """
    client = oauth.Client(consumer)
    response, content = client.request(request_token_url, 'GET')
    if response['status'] != '200':
        raise Exception('Whoops. Invalid response from Twitter.')
    request.session['request_token'] = dict(cgi.parse_qsl(content))
    url = '%s?oauth_token=%s' % (authenticate_url, request.session['request_token']['oauth_token'])
    return redirect(url)


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


def twitter_login(request, template_name='twitter/login.html'):
    """
    Handles authentication with Twitter's OAuth authentication platform.

    If the authenticated user does not yet have a ``User`` registered, they
    are redirected to the Twitter registration backend.

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
    client = oauth.Client(consumer, token)
    response, content = client.request(access_token_url, 'GET')
    if response['status'] != '200':
        raise Exception('Invalid response from Twitter.')
    access_token = dict(cgi.parse_qsl(content))

    # Everything looks to have gone well. So we're going to authenticate the
    # user, if that works, we'll grab some information about them.
    try:
        user = authenticate(twitter_id=access_token['user_id'])
    except:
        # ``authenticate()`` didn't work, and the user is new, so let's send
        # them to registration to set a username and password.
        request.session['twitter_id'] = access_token['user_id']
        return redirect('twitter-setup')
    else:
        # ``authenticate()`` worked and the user has a TwitterProfile already,
        # so let's fetch it and log them in.
        if user is not None:
            try:
                twitter_user = twitter.Twitter().users.show(id=access_token['user_id'])
                avatar = twitter_user['profile_image_url']
            except:
                avatar = ''
            profile = TwitterProfile.objects.get(twitter_id=access_token['user_id'])
            profile.access_token = {
                'oauth_token': access_token['oauth_token'],
                'oauth_token_secret': access_token['oauth_token_secret']
            }
            profile.avatar = avatar
            profile.save()
            if user.is_active:
                login(request, user)
                messages.success(request, 'Welcome back! You have been logged in!')
                return redirect('site-home')
        # ``authenticate()`` didn't work, so we have an existing user trying
        # to connect, but they don't have a TwitterProfile yet, so let's
        # create one. We don't need to log them in though since they've
        # already done so.
        elif request.user.is_authenticated():
            user = request.user
            try:
                twitter_user = twitter.Twitter().users.show(id=access_token['user_id'])
                avatar = twitter_user['profile_image_url']
            except:
                avatar = ''
            profile = TwitterProfile.objects.create(
                user=user,
                twitter_id=access_token['user_id'],
                access_token={
                    'oauth_token': access_token['oauth_token'],
                    'oauth_token_secret': access_token['oauth_token_secret']
                },
                avatar=avatar
            )
            messages.success(request, 'Your Twitter account has been linked with your Hello! Ranking account.')
            return redirect('edit-profile')

    return render_to_response(template_name, {}, context_instance=RequestContext(request))

