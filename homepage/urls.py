from django.urls import path, URLResolver
from homepage.views import homepage, subcategory_user, subcategory_worker, get_categories_and_subcategories
urlpatterns: list[URLResolver] = [
    path('', homepage, name='homepage'),
    path('subcategory_user', subcategory_user, name='subcategory_user'),
    path('subcategory_worker', subcategory_worker, name='subcategory_worker'),
    path('categories/', get_categories_and_subcategories, name='categories'),
]   