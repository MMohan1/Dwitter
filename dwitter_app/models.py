# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import hashlib


class Dweet(models.Model):
    content = models.CharField(max_length=140, unique=True)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def gravatar_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')
    follow_date = models.DateTimeField(auto_now=True)


#User.follow = property(lambda u: Follow.objects.filter(user=u))


class Likes(models.Model):
    dwitte = models.ForeignKey(Dweet)
    likes = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True)


class Comments(models.Model):
    dwitte = models.ForeignKey(Dweet)
    comment_by = models.ForeignKey(User)
    comment = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)
