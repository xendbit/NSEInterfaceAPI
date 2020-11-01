from django.contrib.auth.hashers import make_password
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import models, serializers, utils


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
