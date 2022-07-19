from django.contrib import admin
from .models import ArtExchangeUser, ArtListing, AssetTransfer, BankAccount, BankTransaction, PendingAssetTransfer, User

admin.site.register(ArtExchangeUser)
admin.site.register(ArtListing)
admin.site.register(AssetTransfer)
admin.site.register(BankAccount)
admin.site.register(BankTransaction)
admin.site.register(PendingAssetTransfer)
admin.site.register(User)
