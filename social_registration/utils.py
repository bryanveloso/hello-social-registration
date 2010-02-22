import exceptions
import oauth2 as oauth

from django.conf import settings

try:
    import json
except ImportError:
    from django.utils import simplejson as json


signature_method = oauth.SignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')

REQUEST_TOKEN_URL = getattr(settings, 'OAUTH_REQUEST_TOKEN_URL', 'https://%s/oauth/request_token' % (SERVER,))
ACCESS_TOKEN_URL = getattr(settings, 'OAUTH_ACCESS_TOKEN_URL', 'https://%s/oauth/access_token' % (SERVER,))
AUTHORIZATION_URL = getattr(settings, 'OAUTH_AUTHORIZATION_URL', 'http://%s/oauth/authorize' % (SERVER,))

CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', 'YOUR_KEY')
CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', 'YOUR_SECRET')

# We use this URL to check if Twitter's oAuth worked.
TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'
TWITTER_TIMELINE = 'http://twitter.com/statuses/user_timeline/%s.json'

class TwitterException(exceptions.Exception):
    """
    If a call to Twitter's RESTful API returns anything other than "200 OK,"
    raise this exception to pass the HTTP status and payload to the caller.

    """
    def __init__(self, status, reason, payload):
        self.args = (status, reason, payload)
        self.status = status
        self.reason = reason
        self.payload = payload


def request_oauth_resource(consumer, url, access_token, parameters=None, signature_method=signature_method, http_method='GET'):
    """
    Returns an OAuthRequest object.

    """
    oauth_request = oauth.Request.from_consumer_and_token(consumer, token=access_token, http_method=http_method, http_url=url, parameters=parameters)
    oauth_request.sign_request(signature_method, consumer, access_token)
    return oauth_request


def fetch_response(oauth_request, connection):
    url = oauth_request.to_url()
    connection.request(oauth_request.http_method, url)
    response = connection.getresponse()
    s = response.read()
    if response.status != 200:
        raise TwitterException(response.status, response.reason, s)
    return s


def get_unauthorized_request_token(consumer):
    client = oauth.Client(consumer)
    resp, token = client.request(REQUEST_TOKEN_URL, 'GET')
    return oauth.Token.from_string(token)


def get_authorization_url(consumer, token, signature_method=signature_method):
    oauth_request = oauth.Request.from_consumer_and_token(consumer, token=token, http_url=AUTHORIZATION_URL)
    oauth_request.sign_request(signature_method, consumer, token)
    return oauth_request.to_url()


def exchange_request_token_for_access_token(consumer, connection, request_token, signature_method=signature_method):
    oauth_request = oauth.Request.from_consumer_and_token(consumer, token=request_token, http_url=ACCESS_TOKEN_URL)
    oauth_request.sign_request(signature_method, consumer, request_token)
    resp = fetch_response(oauth_request, connection)
    return oauth.Token.from_string(resp)


def is_authenticated(consumer, connection, access_token):
    oauth_request = request_oauth_resource(consumer, TWITTER_CHECK_AUTH, access_token)
    response_json = fetch_response(oauth_request, connection)
    if 'screen_name' in response_json:
        return json.loads(json)
    return False

