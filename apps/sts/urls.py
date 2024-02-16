from django.urls import path, include
from .views import *

app_name = 'sts'

urlpatterns = [
    # path('admin/confirm-bulk-update/', confirm_bulk_update, name='confirm_bulk_update'),
    # path('admin/perform-bulk-update/', perform_bulk_update, name='perform-custom-action'),
    # path('bulk-actions/', BulkActionsView.as_view(), name='bulk-actions'),
    # path('bulk-clone-ratio-sets/', bulk_clone_ratio_set_view, name='bulk-clone-ratio-sets'),
    #
    # path('locations/', LocationListView.as_view(), name='locations-list'),
    # path('locations/create/', LocationCreateView.as_view(), name='locations-add'),
    # path('locations/<pk>/', LocationDetailsView.as_view(), name='locations-detail'),
    # path('locations/<pk>/update/', LocationUpdateView.as_view(), name='locations-update'),
    # path('locations/<pk>/delete/', LocationsDeleteView.as_view(), name='locations-delete'),
    #
    # path('search-locations/', SearchLocationListView.as_view(), name='search-locations-list'),
    # path('search-locations/create/', SearchLocationCreateView.as_view(), name='search-locations-add'),
    # path('search-locations/<pk>/update', SearchLocationUpdateView.as_view(), name='search-locations-update'),
    # path('search-locations/<pk>/', SearchLocationDetailsView.as_view(), name='search-locations-detail'),
    # path('search-locations/<pk>/delete/', SearchLocationsDeleteView.as_view(), name='search-locations-delete'),
    #
    # path('ratio-sets/', RatioSetListView.as_view(), name='ratio-set-list'),
    # path('ratio-sets/create/', RatioSetCreateView.as_view(), name='ratio-set-add'),
    # path('ratio-sets/<pk>/', RatioSetDetailsView.as_view(), name='ratio-set-detail'),
    # path('ratio-sets/<pk>/update/', RatioSetUpdateView.as_view(), name='ratio-set-update'),
    # path('ratio-sets/<pk>/delete/', RatioSetDeleteView.as_view(), name='ratio-set-delete'),
    #
    # path('brand-location-ratio-sets/', BrandLocationRatioSetListView.as_view(), name='brand-location-ratio-set-list'),
    # path('brand-location-ratio-sets/create/', BrandLocationRatioSetCreateView.as_view(), name='brand-location-ratio-set-add'),
    # path('brand-location-ratio-sets/bulk-update/', BulkUpdateBrandLocationRatioSetView.as_view(), name='brand-location-ratio-set-bulk-update'),
    # path('brand-location-ratio-sets/bulk-create/', BulkCreateBrandLocationRatioSetView.as_view(), name='brand-location-ratio-set-bulk-create'),
    # path('brand-location-ratio-sets/<pk>/', BrandLocationRatioSetDetailsView.as_view(), name='brand-location-ratio-set-detail'),
    # path('brand-location-ratio-sets-history/<pk>/', BrandLocationRatioSetHistoryView.as_view(), name='brand-location-ratio-set-history'),
    # path('brand-location-ratio-sets/<pk>/update/', BrandLocationRatioSetUpdateView.as_view(), name='brand-location-ratio-set-update'),
    # path('brand-location-ratio-sets/<pk>/clone/', CloneBrandLocationRatioSetView.as_view(), name='brand-location-ratio-set-clone'),
    # path('brand-location-ratio-sets-bulk-clone/', BrandLocationRatioSetBulkCloneView.as_view(), name='brand-location-ratio-set-bulk-clone'),
    # path('brand-location-ratio-sets/<pk>/delete/', BrandLocationRatioSetDeleteView.as_view(), name='brand-location-ratio-set-delete'),
    # path('check-s3-ratio-set-status/', S3RatioSetJsonStatusView.as_view(), name='check-s3-ratio-set-status'),
    # path('invalid-and-cache-again/<site_key>', InvalidAndCache.as_view(), name='invalid-and-cache-again'),
]
