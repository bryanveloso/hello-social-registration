from django.contrib.auth import authenticate
from django.db import models


class Association(models.Model):
    """
    A "profile-like" model which stores a service's identifier for a user if
    they have chosen to authenticate with the given service, either during
    registration or after the fact.

    """
    SERVICE_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter')
    )

    user = models.ForeignKey('auth.User')
    service = models.CharField(choices=SERVICE_CHOICES, max_length=10)
    identifier = models.PositiveIntegerField()
    access_token = models.CharField(blank=True, max_length=255)
    avatar = models.CharField(blank=True, max_length=255)
    profile_url = models.URLField(verify_exists=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s: %s' % (self.user, self.identifier)

    def authenticate(self):
        if self.is_active:
            return authenticate(identifier=self.identifier)


