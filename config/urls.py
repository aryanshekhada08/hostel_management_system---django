"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from .views import about, home
# app_name = "accounts"
    
urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('admissions/', include('apps.admissions.urls')),
    # path('accounts/', include('apps.accounts.urls')),
    # path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path(
        'accounts/',
        include(('apps.accounts.urls', 'accounts'), namespace='accounts')
    ),
    path('rooms/', include('apps.rooms.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('fees/', include('apps.fees.urls')),

    path('', home, name='home'),
    path('about/', about, name='about'),
    path('wallet/', include('apps.wallets.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

