# import logging
# import warnings
from facebook import FacebookError
from urllib2 import URLError

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template import TemplateSyntaxError

from models import FacebookProfile


class FacebookConnectMiddleware(object):
    """
    Middleware that provides a working Facebook object.

    """
    def process_request(self, request):
        try:
            # This is true if anyone has ever used the browser to log into
            # Facebook with an account that has accepted this application.
            bona_fide = request.facebook.check_session(request)
            if bona_fide and request.facebook.uid:
                user = request.user
                if user.is_anonymous():
                    # The user should be sent to finish setting up.
                    setup_redirect = reverse('facebook-setup')
                    if request.path != setup_redirect:
                        request.facebook.session_key = None
                        request.facebook.uid = None
            else:
                # We have no Facebook info, so we shouldn't have an FB only
                # user logged in.
                user = request.user
                if user.is_authenticated and bona_fide:
                    try:
                        facebook_profile = FacebookProfile.objects.get(user=user)
                    except FacebookProfile.DoesNotExist, ex:
                        pass
        except Exception, ex:
            logout(request)
            request.facebook.session_key = None
            request.facebook.uid = None
            # warnings.warn('Facebook Connect Middleware Failed -- Reason: %s' % (ex))
            # logging.exception('Facebook Connect Middleware -- Something went "uh oh."')
        return None

    def process_exception(self, request, exception):
        processed_exception = exception
        if type(exception) == TemplateSyntaxError:
            if getattr(exception, 'exc_info', False):
                processed_exception = exception.exc_info[1]
        if type(processed_exception) == FacebookError:
            # We get this error if the Facebook session is timed out.
            # We should log the user out and send them somewhere useful.
            if processed_exception.code is 102:
                logout(request)
                request.facebook.session_key = None
                request.facebook.uid = None
                # logging.error('Facebook Connect Middleware -- Code 102')
                return redirect('facebook-login')
        elif type(processed_exception) == URLError:
            if processed_exception is 104:
                # logging.error('Facebook Connect Middleware -- Code 104, Connection Reset')
                pass
            elif processed_exception is 102:
                # logging.error('Facebook Connect Middleware -- Code 102, Name or Service Not Known')
                pass

