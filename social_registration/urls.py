from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('',

    # Facebook Authentication
    url(r'^facebook/login/$',
        view    = 'social_registration.views.facebook_authentication',
        name    = 'facebook-authentication'
    ),
    url(r'^xd_receiver.html$',
        view    = 'django.views.generic.simple.direct_to_template',
        kwargs  = {
            'template': 'facebook/xd_receiver.html'
        },
        name    = 'facebook-receiver'
    ),

    # Twitter Authentication
    url(r'^twitter/login/$',
        view    = 'social_registration.views.twitter_login',
        name    = 'twitter-login'
    ),
    url(r'^twitter/authorize/$',
        view    = 'social_registration.views.twitter_authorization',
        name    = 'twitter-authorization'
    ),
    url(r'^twitter/unauthorize/$',
        view    = 'social_registration.views.twitter_unauthorization',
        name    = 'twitter-unauthorization'
    )

)

