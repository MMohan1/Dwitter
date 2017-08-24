"""dwitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from dwitter_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),  # root
    url(r'^login$', views.login_view),  # login
    url(r'^logout$', views.logout_view),  # logout
    url(r'^signup$', views.signup),  # signup
    url(r'^dwiters$', views.public),  # public dwitter
    url(r'^submit$', views.submit),  # submit new dwitter
    url(r'^users/$', views.users),  # view user list
    url(r'^users/(?P<username>\w{0,30})/$', views.users),  # Perticuler user view
    url(r'^follow$', views.follow),  # follow user
    url(r'^like$', views.like),  # like the dwitte
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
