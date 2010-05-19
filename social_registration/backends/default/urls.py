from django.conf.urls.defaults import *


urlpatterns = patterns('',

    url(r'^login/$',
        view    = 'social_registration.views.login',
        kwargs  = {
            'template_name': 'accounts/login.html'
        },
        name    = 'login'
    ),
    url(r'^logout/$',
        view    = 'social_registration.views.logout_then_login',
        name    = 'logout'
    ),
    url(r'^password/change/$',
        view    = 'django.contrib.auth.views.password_change',
        name    = 'password-change'
    ),
    url(r'^password/change/done/$',
        view    = 'django.contrib.auth.views.password_change_done',
        name    = 'password-change-done'
    ),
    url(r'^password/reset/$',
        view    = 'django.contrib.auth.views.password_reset',
        name    = 'password-reset'
    ),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        view    = 'django.contrib.auth.views.password_reset_confirm',
        name    = 'password-reset-confirm'
    ),
    url(r'^password/reset/complete/$',
        view    = 'django.contrib.auth.views.password_reset_complete',
        name    = 'password-reset-complete'
    ),
    url(r'^password/reset/done/$',
        view    = 'django.contrib.auth.views.password_reset_done',
        name    = 'password-reset-done'
    )

)


