# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from dwitter_app.forms import AuthenticateForm, UserCreateForm, DwitterForm
from dwitter_app.models import Dweet, Likes, Comments, Follow
from django.conf import settings
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q


def index(request, auth_form=None, user_form=None, dwitter_form=None):
    """
    view is used to get the home page for app
    """
    # User is logged in
    if request.user.is_authenticated():
        dwitter_form = dwitter_form or DwitterForm()
        user = request.user
        query_string = request.GET.get("q")
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True).distinct()
        if not query_string:
            query_string = request.POST.get("query")
            if query_string == "None":
                query_string = None
        if query_string:
            dwitters = Dweet.objects.filter(
                Q(user__in=following_users) | Q(user=user.id), content__icontains=query_string).annotate(num_likes=Count('likes',distinct=True)).annotate(num_comments=Count("comments",distinct=True))
        else:
            dwitters = Dweet.objects.filter(Q(user__in=following_users) | Q(user=user.id)).annotate(num_likes=Count('likes',distinct=True)).annotate(num_comments=Count("comments",distinct=True))
        return render(request,
                      'buddies.html',
                      {'dwitter_form': dwitter_form, 'user': user,
                       'dwitters': dwitters[::-1],
                       "query_string": query_string,
                       'next_url': '/', "STATIC_URL": settings.STATIC_URL})
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
        return index(request, user_form=user_form)
    return redirect('/')


@login_required
def public(request, dwitter_form=None):
    """
    view is used to get the public dwitte
    """
    dwitter_form = dwitter_form or DwitterForm()
    dwiters = Dweet.objects.all()[::-1]
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
        return user.dweet_set.order_by('-id')[0]
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
        dwiters = Dweet.objects.filter(user=user.id)
        if username == request.user.username or user.following.filter(following=request.user):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'dwiters': dwiters, "STATIC_URL": settings.STATIC_URL})
        return render(request, 'user.html', {'user': user, 'dwiters': dwiters, 'follow': True, "STATIC_URL": settings.STATIC_URL})
    query_string = request.GET.get("q")
    if query_string:
        users = User.objects.filter(username__icontains=query_string).annotate(dwiters_count=Count('dweet'))
    else:
        users = User.objects.all().annotate(dwiters_count=Count('dweet'))
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
                Follow(follower=request.user, following=user).save()
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
                dwitter = Dweet.objects.get(id=dwitter_id)
                dl = Likes(dwitte=dwitter, likes=request.user)
                dl.save()
            except ObjectDoesNotExist:
                return redirect('/')
            except IntegrityError:
                dwitter_form = DwitterForm()
                dwitter_form.errors["content"] = "Hey " + \
                    request.user.first_name + "You are all ready liked this dwitte"
                return index(request, dwitter_form=dwitter_form)
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
                dwitter = Dweet.objects.get(id=dwitter_id)
                dl = Comments(dwitte=dwitter, comment_by=request.user)
                dl.comment = comment
                dl.save()
            except ObjectDoesNotExist:
                return redirect('/')
    return index(request)


@login_required
def activity(request):
    """
    """
    tmp_str = "YET TO COME"
    return render(request, "activity.html", {"tmp_str": tmp_str, "STATIC_URL": settings.STATIC_URL})
