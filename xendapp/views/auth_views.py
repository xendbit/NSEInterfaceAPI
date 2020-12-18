import os
from django.contrib.auth.hashers import make_password
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from .. import models, serializers, utils, permissions
from . import providus_views
from ..utils import upload_image

artexchange_email = os.getenv('ARTEXCHANGE_EMAIL')

class UserList(generics.ListCreateAPIView):
    """
        get:
        Return the list of all user objects

        post:
        create a new user
    """

    queryset = models.User.objects.filter(is_deleted=False)
    # permission_classes = [permissions.IsXendAdmin]
    serializer_class = serializers.UserSerializer
    # parser_classes = [FormParser, MultiPartParser, JSONParser]

    def post(self, request):

        data = request.data
        # data = data.copy()
        # img = data.get('image_url')
        # data['image_url'] = upload_image(img) if img else ''
        #
        # id_img = data.get('id_image_url')
        # data['id_image_url'] = upload_image(id_img) if id_img else ''

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['password'] = make_password(data.get('password'))
        serializer.validated_data['username'] = serializer.validated_data.get('email')
        serializer.validated_data['is_active'] = False
        del serializer.validated_data['confirm_password']

        bvn = serializer.validated_data.get('bvn')
        email = serializer.validated_data.get('email')
        full_name = serializer.validated_data.get('full_name')
        firstname = full_name.split(' ')[0]
        providus_contract_code = os.getenv('PROVIDUS_CONTRACT_CODE')

        data = {
            'accountReference': f'{bvn}_{firstname}',
            'accountName': full_name,
            'currencyCode': "NGN",
            'contractCode': providus_contract_code,
            'customerEmail': email,
            'customerName': full_name
        }

        resp_json, statuss, bank = providus_views.providus_reserve_account(data)
        serializer.validated_data['wallet_account_number'] = resp_json['Message']['AccountNumber']
        serializer.save()

        payload = {
            'message': "Successfully signed up",
            'data': serializer.data
        }
        return Response(payload, status=status.HTTP_201_CREATED)


@api_view()
@permission_classes([permissions.IsXendAdmin])
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


class PasswordUpdateView(UpdateAPIView):
    """
    put:
        Update a user password
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.PasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)


        current_password = serializer.validated_data.get("current_password")
        if not self.object.check_password(current_password):
            return Response({'detail': 'The current password provided is not correct'}, status=400)
        self.object.set_password(serializer.validated_data.get("new_password"))
        self.object.save()
        return Response({'detail': 'password change successful'}, status=200)
