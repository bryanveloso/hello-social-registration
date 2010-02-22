from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink


class FacebookProfile(models.Model):
    """
    A profile which stores a Facebook user ID for a user if they have chosen
    to use Facebook Connect during registration or after the fact.

    """
    user = models.ForeignKey(User)
    uid = models.IntegerField(unique=True)
    avatar = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s: %s' % (self.user, self.uid)

    @permalink
    def get_absolute_url(self):
        return 'http://facebook.com/profile.php?id=%s' % (self.uid)

    def authenticate(self):
        return authenticate(uid=self.uid)


class TwitterProfile(models.Model):
    """
    A profile which stores a Twitter user ID for a user if they have chosen
    to use Twitter to register or the user connects Twitter to their account
    after the fact.

    """
    user = models.ForeignKey(User)
    twitter_id = models.PositiveIntegerField()
    access_token = models.CharField(max_length=255, blank=True)
    avatar = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s: %s' % (self.user, self.twitter_id)

    def authenticate(self):
        return authenticate(twitter_id=self.twitter_id)

