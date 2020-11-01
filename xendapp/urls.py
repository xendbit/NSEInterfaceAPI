from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import artexchange_views, auth_views
urlpatterns = [
    path('artexchange/new-user', artexchange_views.user_registration, name='artuser_registration'),
    path('artexchange/buy-request', artexchange_views.asset_buy_request, name='buy_request'),
    path('users/signup', auth_views.UserList.as_view() , name='signup'),
    path('users/role/<int:pk>', auth_views.manage_user_roles, name='assign_role'),
    path('users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token-refresh', TokenRefreshView.as_view(), name='token_refresh'),
]