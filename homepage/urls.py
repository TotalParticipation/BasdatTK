from django.urls import path, URLResolver
from homepage.views import homepage, subcategory_user, subcategory_worker, get_categories_and_subcategories, subcategory_detail
urlpatterns: list[URLResolver] = [
    path('', homepage, name='homepage'),
    path('subcategory_user/<int:uuid>', subcategory_user, name='subcategory_user'),
    path('subcategory_worker/<int:uuid>', subcategory_worker, name='subcategory_worker'),
    path('categories/', get_categories_and_subcategories, name='categories'),
     path('subcategory/<uuid:subcategory_id>/', subcategory_detail, name='subcategory_detail'),
]   