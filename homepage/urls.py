from django.urls import path, URLResolver
from views import homepage, subcategory_view
urlpatterns: list[URLResolver] = [
    path('', homepage, name='homepage'),
    path('subcategory', subcategory_view, name='subcategory'),
]   