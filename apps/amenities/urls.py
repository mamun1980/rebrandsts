from django.urls import path
from apps.amenities.views import (
    AmenityTypeListView, AmenityTypeCreateView, AmenityTypeDetailView, AmenityTypeDeleteView, AmenityTypeUpdateView,
    AmenityTypeMappingView, PartnerAmenityTypeListView, PartnerAmenityCreateView, PartnerAmenityDetailView,
    PartnerAmenityDeleteView, PartnerAmenityUpdateView
)


urlpatterns = [
    # LeftTravel amenities path
    path('amenity-type-list/', AmenityTypeListView.as_view(), name='amenity-type-list'),
    path('add-amenity-type/', AmenityTypeCreateView.as_view(), name='add-amenity-type'),
    path('amenity-type-detail/<pk>/', AmenityTypeDetailView.as_view(), name='amenity-type-detail'),
    path('amenity-type-update/<pk>/', AmenityTypeUpdateView.as_view(), name='amenity-type-update'),
    path('amenity-type-delete/<pk>/', AmenityTypeDeleteView.as_view(), name='amenity-type-delete'),
    # Partner amenities paths
    path('partner-amenity-type-list/', PartnerAmenityTypeListView.as_view(), name='partner-amenity-type-list'),
    path('add-partner-amenity-type/', PartnerAmenityCreateView.as_view(), name='add-partner-amenity-type'),
    path('partner-amenity-type-detail/<pk>/', PartnerAmenityDetailView.as_view(), name='partner-amenity-type-detail'),
    path('partner-amenity-type-update/<pk>/', PartnerAmenityUpdateView.as_view(), name='partner-amenity-type-update'),
    path('partner-amenity-type-delete/<pk>/', PartnerAmenityDeleteView.as_view(), name='partner-amenity-type-delete'),
    # amenity type mapping
    path('amenity-type-mapping/', AmenityTypeMappingView.as_view(), name='amenity-type-mapping'),
]
