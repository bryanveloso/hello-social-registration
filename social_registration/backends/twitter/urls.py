"""
URLconf for registration and activation, using the Twitter OAuth custom
registration backend.

"""
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import activate, register


urlpatterns = patterns('',

    url(r'^twitter/setup/$',
        view    = register,
        kwargs  = {
            'backend': 'registration.backends.twitter.TwitterBackend',
            'template_name': 'twitter/user_form.html'
        },
        name    = 'twitter-setup'
    ),
    url(r'^twitter/complete/$',
        view    = direct_to_template,
        kwargs  = {
            'template': 'registration/registration_complete.html'
        },
        name    = 'twitter-registration-complete'
    ),
    url(r'^twitter/closed/$',
        view    = direct_to_template,
        kwargs  = {
            'template': 'registration/registration_closed.html'
        },
        name    = 'twitter-registration-closed'
    )

)

