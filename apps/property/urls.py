from django.urls import path
from .views import (PropertyTypeListView, PropertyTypeDetailsView, PropertyTypeCreateView, PropertyTypeDeleteView,
                    PropertyTypeUpdateView, PartnerPropertyTypeListView, PartnerPropertyTypeCreateView,
                    PartnerPropertyTypeDetailsView, PartnerPropertyTypeDeleteView, PartnerPropertyTypeUpdateView,
                    PartnerPropertyMappingListView, PartnerPropertyMappingCreateView, PartnerPropertyMappingDetailsView,
                    PartnerPropertyMappingDeleteView, DragAndDropPartnerPropertyMappingView)

urlpatterns = [
    path('property-types/', PropertyTypeListView.as_view(), name='property-types-list'),
    path('property-types/create/', PropertyTypeCreateView.as_view(), name='property-types-add'),
    path('property-types/<pk>/', PropertyTypeDetailsView.as_view(), name='property-types-detail'),
    path('property-types/<pk>/update/', PropertyTypeUpdateView.as_view(), name='property_types_update'),
    path('property-types/<pk>/delete/', PropertyTypeDeleteView.as_view(), name='property-types-delete'),

    path('partner-property-types/', PartnerPropertyTypeListView.as_view(), name='partner-property-types-list'),
    path('partner-property-types/create/', PartnerPropertyTypeCreateView.as_view(), name='partner-property-types-add'),
    path('partner-property-types/<pk>/update/', PartnerPropertyTypeUpdateView.as_view(),
         name='partner-property-types-update'),
    path('partner-property-types/<pk>/', PartnerPropertyTypeDetailsView.as_view(), name='partner-property-types-detail'),
    path('partner-property-types/<pk>/delete/', PartnerPropertyTypeDeleteView.as_view(),
         name='partner-property-types-delete'),

    path('partner-property-mappings/', PartnerPropertyMappingListView.as_view(), name='partner-property-mapping-list'),
    path('partner-property-mappings/create/', PartnerPropertyMappingCreateView.as_view(), name='property-mapping-add'),
    path('partner-property-mappings/<pk>/', PartnerPropertyMappingDetailsView.as_view(), name='property-mapping-detail'),
    path('partner-property-mappings/<pk>/delete/', PartnerPropertyMappingDeleteView.as_view(), name='property-mapping-delete'),
    path(
        'drag-and-drop-partner-property-mapping/',
        DragAndDropPartnerPropertyMappingView.as_view(),
        name='drag-and-drop-partner-property-mapping'
    ),
]
