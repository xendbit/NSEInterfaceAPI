import os
from django.contrib.auth.hashers import make_password
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from .. import models, serializers, utils, permissions

artexchange_email = os.getenv('ARTEXCHANGE_EMAIL')

class UserList(generics.ListCreateAPIView):
    """
        get:
        Return the list of all user objects

        post:
        create a new user when logged in as an admin
    """

    queryset = models.User.objects.filter(is_deleted=False)
    # permission_classes = [IsAuthenticated]
    serializer_class = serializers.AdminCreateUserSerializer

    def post(self, request):

        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['password'] = make_password(data.get('password'))
        serializer.validated_data['username'] = serializer.validated_data.get('email')
        serializer.validated_data['is_active'] = False
        del serializer.validated_data['confirm_password']
        serializer.save()

        payload = {
            'message': "Successfully signed up",
            'data': serializer.data
        }
        return Response(payload, status=status.HTTP_201_CREATED)


@api_view()
# @permission_classes([permissions.IsXendAdmin])
def manage_user_roles(request, pk):
    '''Assign a role to a user'''

    ROLE_CHOICES = ['System Admin', None]

    new_role = request.query_params.get('new_role')
    if new_role not in ROLE_CHOICES:
        raise ValueError(f'{new_role} is not an acceptable value for the role field. Choose from {ROLE_CHOICES}')

    user = models.User.objects.get(id=pk)
    user.role = new_role
    user.is_active = True
    user.full_clean()
    user.save()

    return Response({'detail': 'Role successfully set'}, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    '''Blacklists a refresh token'''

    refresh_token = request.data["refresh_token"]
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as exec:
        return Response({'detail': str(exec)}, status=status.HTTP_400_BAD_REQUEST)


@api_view()
@permission_classes([permissions.IsXendAdmin])
def get_token(request):
    '''returns a token for the ArtExchange user'''
    user = models.User.objects.get(email=artexchange_email)
    existing_tokens = Token.objects.filter(user_id=user.id)
    if existing_tokens.exists():
        for token in existing_tokens:
            token.delete()
    token = Token.objects.create(user=user)

    return Response({ 'token' : str(token) })