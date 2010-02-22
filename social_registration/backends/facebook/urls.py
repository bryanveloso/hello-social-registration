"""
URLconf for registration and activation, using the Facebook Connect custom
registration backend.

"""
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import activate, register


urlpatterns = patterns('',

    url(r'^facebook/setup/$',
        view    = register,
        kwargs  = {
            'backend': 'registration.backends.facebook.FacebookBackend',
            'template_name': 'registration/facebook/user_form.html'
        },
        name    = 'facebook-setup'
    ),
    url(r'^facebook/complete/$',
        view    = direct_to_template,
        kwargs  = {
            'template': 'registration/registration_complete.html'
        },
        name    = 'facebook-registration-complete'
    ),
    url(r'^facebook/closed/$',
        view    = direct_to_template,
        kwargs  = {
            'template': 'registration/registration_closed.html'
        },
        name    = 'facebook-registration-closed'
    )

)

