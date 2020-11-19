from rest_framework import generics

from xendapp import serializers, models, filters


class AssetUserListView(generics.ListAPIView):
    '''All Asset Users'''

    serializer_class = serializers.RegistrationSerializer
    filterset_class = filters.AssetsUserFilter

    def get_queryset(self):
        return models.ArtExchangeUser.objects.filter(is_deleted=False)


class AssetTransferListView(generics.ListAPIView):
    '''All Asset Transfers'''

    serializer_class = serializers.AssetTransferSerializer
    filterset_class = filters.AssetTransferFilter

    def get_queryset(self):
        return models.AssetTransfer.objects.filter(is_deleted=False).order_by('-created_at')


class AssetListingListView(generics.ListAPIView):
    '''All Asset Listings'''

    serializer_class = serializers.AssetListingSerializer
    # filterset_class = filters.AssetTransferFilter

    def get_queryset(self):
        return models.ArtListing.objects.filter(is_deleted=False).order_by('-created_at')



