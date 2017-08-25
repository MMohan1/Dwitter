# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import hashlib
 
 
class Dwitter(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)
 
 
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)
 
    def gravatar_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()
 
 
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class DwitterLike(models.Model):
    dwitte = models.ForeignKey(Dwitter)
    likes = models.ManyToManyField(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)


class DwitterComment(models.Model):
    dwitte = models.ForeignKey(Dwitter)
    comments = models.ManyToManyField(User)
    content = models.TextField(max_length=140)
    creation_date = models.DateTimeField(auto_now=True, blank=True)
