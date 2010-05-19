import facebook

from django.conf import settings


class Facebook(object):
    def __init__(self, user=None):
        if user is None:
            self.identifier = None
        else:
            self.identifier = user['uid']
            self.user = user
            self.graph = facebook.GraphAPI(user['access_token'])


class FacebookMiddleware(object):
    def process_request(self, request):
        """
        Enables ``request.facebook`` and ``request.facebook.graph`` in views
        once the user authenticates the application and connects with Facebook
        Platform.

        """
        facebook_user = facebook.get_user_from_cookie(request.COOKIES, settings.FACEBOOK_API_KEY, settings.FACEBOOK_SECRET_KEY)
        request.facebook = Facebook(facebook_user)
        return None


