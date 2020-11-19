from django import forms
from django_filters import rest_framework as filters


class AssetsUserFilter(filters.FilterSet):
    bank_name = filters.CharFilter(lookup_expr='icontains')
    user_type = filters.ChoiceFilter(widget=forms.Select, field_name='user_type',
                                  choices=(('Investor', 'Investor'), ('Issuer', 'Issuer')))

class AssetTransferFilter(filters.FilterSet):
    seller_id = filters.CharFilter(lookup_expr='exact')
    buyer_id = filters.CharFilter(lookup_expr='exact')
    asset_id = filters.CharFilter(lookup_expr='iexact')
    asset_type = filters.ChoiceFilter(widget=forms.Select, field_name='asset_type',
                                     choices=(('Art', 'Art'), ('Estate', 'Estate')))
