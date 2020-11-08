from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import artexchange_views, auth_views, providus_views
urlpatterns = [
    path('artexchange/new-user', artexchange_views.user_registration, name='artuser_registration'),
    path('artexchange/buy-request', artexchange_views.asset_buy_request, name='buy_request'),
    path('artexchange/listing', artexchange_views.asset_listing, name='listing'),
    path('auth/signup', auth_views.UserList.as_view() , name='signup'),
    path('auth/role/<int:pk>', auth_views.manage_user_roles, name='assign_role'),
    path('auth/login', TokenObtainPairView.as_view(), name='auth_login'),
    path('auth/obtain-token', auth_views.get_token, name='obtain_token'),
    path('auth/token-refresh', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('auth/logout', auth_views.logout, name='auth_logout'),
    path('auth/change-password', auth_views.PasswordUpdateView.as_view(), name='change_password')
]