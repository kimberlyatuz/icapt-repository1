"""
URL configuration for ICAPT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# for the admin dashboard
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
# Override default login URL
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),

    ]
# Internationalized URLs (with language prefix)
urlpatterns += i18n_patterns(
    path('', include('app1.urls')),
    path('ME/', include('ME.urls')),

    # Third-party packages that need translation
    path('accounts/', include('registration.backends.default.urls')),
    path('', RedirectView.as_view(url='/en/', permanent=True)),
)
