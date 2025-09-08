"""
URL configuration for pumpfunproject project.

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
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

########################################################
# pumpfunproject/urls.py

from django.contrib import admin
from django.urls import path
from pumplistener.views import view_log_file, trigger_token_cleanup, preview_email_report
urlpatterns = [
    path('admin/', admin.site.urls),

    # ADD THIS LINE: Creates a URL to access your log view
    # You can change 'view-log/' to any path you want.
    path('view-log/', view_log_file, name='view_log'),
    path('trigger-cleanup-a7g3k9q/', trigger_token_cleanup, name='trigger_cleanup'),
    #######################################
    path('preview-email/', preview_email_report, name='preview_email'),
    #######################################
]