from django.urls import path, URLResolver
from homepage.views import homepage, subcategory_user, subcategory_worker, get_categories_and_subcategories, redirect_to_other_api, subcategory_detail, create_order, view_orders, join_category
urlpatterns: list[URLResolver] = [
    path('', homepage, name='homepage'),
    path('subcategory_user/<int:uuid>', subcategory_user, name='subcategory_user'),
    path('subcategory_worker/<int:uuid>', subcategory_worker, name='subcategory_worker'),
    path('categories/', get_categories_and_subcategories, name='categories'),
    path('subcategory/<uuid:subcategory_id>/', subcategory_detail, name='subcategory_detail'),
    path("create-order/", create_order, name="create_order"),
    path("view-orders/", view_orders, name="view_orders"),
    path("join-category/", join_category, name="join_category"),    
    path('redirect-profile/<str:nohp>/', redirect_to_other_api, name='redirect_profile'),

]   