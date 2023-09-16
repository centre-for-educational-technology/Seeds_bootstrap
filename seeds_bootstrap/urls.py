"""seeds_bootstrap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""SEEDS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views
from register import views as v
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin
urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    path("register/", v.register, name="register"),
    path("password_reset/", v.password_reset_request, name='password_reset'),
    path("password_reset/done", auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset/confirm/<slug:uidb64>/<slug:token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="sign_pwd_reset_step2.html"), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('account_activation_sent/', v.account_activation_sent,
         name='account_activation_sent'),
    path('activate/<slug:uidb64>/<slug:token>/', v.activate, name='activate'),
    path('inspect/<scenario_id>', views.inspect, name='inspect'),
    path('compare/', views.compare, name='compare'),


    path('login/', v.login, name='login'),
    path('logout/', v.logout, name='logout'),
    path('vote/<selection>/<scenario>/', views.vote, name='vote'),
    path('project/', login_required(views.project_page),
         name='project_select_page'),
    path('portfolio/<project_id>',
         login_required(views.portfolio), name='portfolio'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('interface/', login_required(views.selection), name='interface'),
    path('location/', login_required(views.select_location), name='location'),

]
