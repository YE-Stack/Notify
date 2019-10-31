from django.conf.urls import url
from django.urls import path

from .views import home_view

urlpatterns = [
	path('', home_view)
]