"""
URLconf for registration and activation, using the Facebook Connect custom
registration backend.

"""
from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^facebook/setup/$',
        view    = 'registration.views.register',
        kwargs  = {
            'backend': 'registration.backends.facebook.FacebookBackend',
            'template_name': 'facebook/user_form.html'
        },
        name    = 'facebook-setup'
    ),
    url(r'^facebook/complete/$',
        view    = 'django.views.generic.simple.direct_to_template',
        kwargs  = {
            'template': 'registration/registration_complete.html'
        },
        name    = 'facebook-registration-complete'
    ),
    url(r'^facebook/closed/$',
        view    = 'django.views.generic.simple.direct_to_template',
        kwargs  = {
            'template': 'registration/registration_closed.html'
        },
        name    = 'facebook-registration-closed'
    )

)


urlpatterns = patterns('',

    url(r'^facebook/prepare/$',
        view    = 'accounts.views.prepare',
        kwargs  = {
            'backend': 'accounts.backends.facebook.FacebookBackend',
        },
        name    = 'facebook-prepare'
    ),
    url(r'^facebook/authenticate/$',
        view    = 'accounts.views.authenticate',
        kwargs  = {
            'backend': 'accounts.backends.facebook.FacebookBackend',
        },
        name    = 'facebook-authentication'
    ),
    url(r'^facebook/deauthenticate/$',
        view    = 'accounts.views.deauthenticate',
        kwargs  = {
            'backend': 'accounts.backends.facebook.FacebookBackend',
        },
        name    = 'facebook-deauthentication'
    )

)


