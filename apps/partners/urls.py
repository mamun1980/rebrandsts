from django.urls import path
from apps.partners.views import (
    PartnerCreateView, PartnerListView, PartnerDetailsView, PartnerDeleteView, PartnerUpdateView,
    ProviderListView, ProviderDetailsView, ProviderCreateView, ProviderUpdateView, ProviderDeleteView
)


urlpatterns = [
    path('provider/', ProviderListView.as_view(), name='provider-list'),
    path('provider/create/', ProviderCreateView.as_view(), name='provider-add'),
    path('provider/<pk>/', ProviderDetailsView.as_view(), name='provider-detail'),
    path('provider/<pk>/update/', ProviderUpdateView.as_view(), name='provider-update'),
    path('provider/<pk>/delete/', ProviderDeleteView.as_view(), name='provider-delete'),
    # partner
    path('', PartnerListView.as_view(), name='partners-list'),
    path('create/', PartnerCreateView.as_view(), name='partners-add'),
    path('<pk>/', PartnerDetailsView.as_view(), name='partners-detail'),
    path('<pk>/update', PartnerUpdateView.as_view(), name='partners_update'),
    path('<pk>/delete/', PartnerDeleteView.as_view(), name='partners-delete'),
]