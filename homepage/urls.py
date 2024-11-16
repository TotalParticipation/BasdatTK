from django.urls import path, URLResolver
from views import homepage
urlpatterns: list[URLResolver] = [
    path('', homepage, name='homepage'),
]   