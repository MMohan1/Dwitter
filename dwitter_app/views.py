# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from dwitter_app.forms import AuthenticateForm, UserCreateForm, DwitterForm
from dwitter_app.models import Dwitter, DwitterLike, DwitterComment
from django.conf import settings
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist


def index(request, auth_form=None, user_form=None, dwitter_form=None):
    """
    view is used to get the home page for app
    """
    # User is logged in
    if request.user.is_authenticated():
        dwitter_form = dwitter_form or DwitterForm()
        user = request.user
        query_string = request.GET.get("q")
        if not query_string:
            query_string = request.POST.get("query")
            if query_string == "None":
                query_string = None
        if query_string:
            dwitters_self = Dwitter.objects.filter(user=user.id, content__icontains=query_string)
            dwitters_buddies = Dwitter.objects.filter(
                user__userprofile__in=user.profile.follows.all(), content__icontains=query_string)
        else:
            dwitters_self = Dwitter.objects.filter(user=user.id)
            dwitters_buddies = Dwitter.objects.filter(user__userprofile__in=user.profile.follows.all())
        dwitters = dwitters_self | dwitters_buddies
        return render(request,
                      'buddies.html',
                      {'dwitter_form': dwitter_form, 'user': user,
                       'dwitters': dwitters[::-1],
                       "query_string": query_string,
                       'next_url': '/', "STATIC_URL": settings.STATIC_URL})
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, "STATIC_URL": settings.STATIC_URL})


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
    """
    logout
    """
    logout(request)
    return redirect('/')


def signup(request):
    """
    signup view
    """
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


@login_required
def public(request, dwitter_form=None):
    """
    view is used to get the public dwitte
    """
    dwitter_form = dwitter_form or DwitterForm()
    dwiters = Dwitter.objects.all()[::-1]
    return render(request,
                  'public.html',
                  {'dwitter_form': dwitter_form, 'next_url': '/dwiters',
                   'dwiters': dwiters, 'username': request.user.username, "STATIC_URL": settings.STATIC_URL})


@login_required
def submit(request):
    """
    view is used to save the user dwitte
    """
    if request.method == "POST":
        dwitter_form = DwitterForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if dwitter_form.is_valid():
            dwitter = dwitter_form.save(commit=False)
            dwitter.user = request.user
            dwitter.save()
            return redirect(next_url)
        else:
            return index(request, dwitter_form=dwitter_form)
    return redirect('/')


def get_latest(user):
    """
    for a user get the lattest twitte details
    """
    try:
        return user.dwitter_set.order_by('-id')[0]
    except IndexError:
        return ""


@login_required
def users(request, username="", dwitter_form=None):
    """
    view is used to get all user details and a spacific user details
    """
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        dwiters = Dwitter.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'dwiters': dwiters, "STATIC_URL": settings.STATIC_URL})
        return render(request, 'user.html', {'user': user, 'dwiters': dwiters, 'follow': True, "STATIC_URL": settings.STATIC_URL})
    query_string = request.GET.get("q")
    if query_string:
        users = User.objects.filter(username__icontains=query_string).annotate(dwiters_count=Count('dwitter'))
    else:
        users = User.objects.all().annotate(dwiters_count=Count('dwitter'))
    dwites = map(get_latest, users)
    obj = zip(users, dwites)
    dwitter_form = dwitter_form or DwitterForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'dwitter_form': dwitter_form,
                   "query_string": query_string,
                   'username': request.user.username, "STATIC_URL": settings.STATIC_URL})


@login_required
def follow(request):
    """
    view is used to save the follwers details in in DB
    """
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')


@login_required
def like(request):
    """
    view is used to save the user likes with repactive to a dwitte
    """
    if request.method == "POST":
        dwitter_id = request.POST.get('dwitter_id', False)
        if dwitter_id:
            try:
                dwitter = Dwitter.objects.get(id=dwitter_id)
                dl = DwitterLike(dwitte=dwitter)
                dl.save()
                dl.likes.add(request.user)
            except ObjectDoesNotExist:
                return redirect('/')
    return index(request)


@login_required
def comment(request):
    """
    view is used to save the user comment with repactive to a dwitte
    """
    if request.method == "POST":
        dwitter_id = request.POST.get('dwitter_id', False)
        comment = request.POST.get('content', False)
        if dwitter_id:
            try:
                dwitter = Dwitter.objects.get(id=dwitter_id)
                dl = DwitterComment(dwitte=dwitter)
                dl.comment = comment
                dl.save()
                dl.comment_by.add(request.user)
            except ObjectDoesNotExist:
                return redirect('/')
    return index(request)
