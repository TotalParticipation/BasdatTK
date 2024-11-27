from django.urls import path
from zillanAPP import views


urlpatterns = [
    path('login', views.login_view,name='login'), # This maps the '/test/' URL to the test_view function
    path('profile-pelanggan', views.view_profile_pelanggan,name='profile_pelanggan'),
    path('register-pelanggan', views.view_register_pelanggan,name='register_pelanggan'), 
    path('profile-pekerja', views.view_profile_pekerja,name='profile_pekerja'), 
    path('register-pekerja', views.view_register_pekerja,name='register_pekerja'), 
    
    path('logout/', views.logout_view, name='logout'),
]
