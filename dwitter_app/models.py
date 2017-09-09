# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import hashlib


class Dweet(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    # follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def gravatar_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])



class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')
    follow_date = models.DateTimeField(auto_now=True)


#User.follow = property(lambda u: Follow.objects.filter(user=u))


class Likes(models.Model):
    dwitte = models.ForeignKey(Dweet)
    likes = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("dwitte", "likes")


class Comments(models.Model):
    dwitte = models.ForeignKey(Dweet)
    comment_by = models.ForeignKey(User)
    comment = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)
