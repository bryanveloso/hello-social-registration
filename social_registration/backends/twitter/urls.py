"""
URLconf for registration and activation, using the Twitter OAuth custom
registration backend.

"""
from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^twitter/setup/$',
        view    = 'registration.views.register',
        kwargs  = {
            'backend': 'registration.backends.twitter.TwitterBackend',
            'template_name': 'twitter/user_form.html'
        },
        name    = 'twitter-setup'
    ),
    url(r'^twitter/complete/$',
        view    = 'django.views.generic.simple.direct_to_template',
        kwargs  = {
            'template': 'registration/registration_complete.html'
        },
        name    = 'twitter-registration-complete'
    ),
    url(r'^twitter/closed/$',
        view    = 'django.views.generic.simple.direct_to_template',
        kwargs  = {
            'template': 'registration/registration_closed.html'
        },
        name    = 'twitter-registration-closed'
    )

)


urlpatterns += patterns('',

    url(r'^twitter/prepare/$',
        view    = 'social_registration.views.prepare',
        kwargs  = {
            'backend': 'social_registration.backends.twitter.TwitterBackend',
        },
        name    = 'twitter-prepare'
    ),
    url(r'^twitter/authenticate/$',
        view    = 'social_registration.views.authenticate',
        kwargs  = {
            'backend': 'social_registration.backends.twitter.TwitterBackend',
        },
        name    = 'twitter-authenticate'
    ),
    url(r'^twitter/deauthenticate/$',
        view    = 'social_registration.views.deauthenticate',
        kwargs  = {
            'backend': 'social_registration.backends.twitter.TwitterBackend',
        },
        name    = 'twitter-deauthenticate'
    )

)


