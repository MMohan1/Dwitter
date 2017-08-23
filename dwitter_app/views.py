# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from dwitter_app.forms import AuthenticateForm, UserCreateForm, DwitterForm
from dwitter_app.models import Dwitter
from django.conf import settings


def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        dwitter_form = DwitterForm()
        user = request.user
        dwitters_self = Dwitter.objects.filter(user=user.id)
        dwitters_buddies = Dwitter.objects.filter(user__userprofile__in=user.profile.follows.all())
        dwitters = dwitters_self | dwitters_buddies
 
        return render(request,
                      'buddies.html',
                      {'dwitter_form': dwitter_form, 'user': user,
                       'ribbits': dwitters,
                       'next_url': '/', "STATIC_URL":settings.STATIC_URL})
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, "STATIC_URL":settings.STATIC_URL})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')
 
 
def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password2']
            # username = user_form.clean_username()
            # password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')