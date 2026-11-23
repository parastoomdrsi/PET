from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('expenses.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
]
