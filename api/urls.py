from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts import views

from .views import (
    LocationViewSet, RatioSetViewSet, SQSTermViewSet, PropertyGroupViewSet, PartnerProviderViewSet, SetWithRatioViewSet,
    RatioGroupViewSet, StaticSiteMapUrlAPIView, DynamicSiteMapUrlAPIView, PartnerAPIView, GetSTSConfigViewSet,
    GetMappedPropertyTypeAPIView, NewGetSTSConfigViewSetMT, PropertyTypeRefressAPIView, LeaveBehindPopUnderRulesAPIView
)

from api.views import (
    AmenityTypeRefresh, AmenityTypeUpdateDeleteView, PartnerAmenityTypeRefresh, PartnerAmenityTypeUpdateDeleteView
)


router = DefaultRouter()
router.register(r'partners', PartnerAPIView)
router.register(r'ratio-set', RatioSetViewSet)
router.register(r'ratio-group', RatioGroupViewSet)
router.register(r'ratio-set', RatioSetViewSet)
router.register(r'get-locations', LocationViewSet)
router.register(r'get-sqs-terms', SQSTermViewSet)
router.register(r'property-group', PropertyGroupViewSet)
router.register(r'get-kayak-provider-order', PartnerProviderViewSet)
router.register(r'get-static-sitemap-urls', StaticSiteMapUrlAPIView)
router.register(r'get-dynamic-sitemap-urls', DynamicSiteMapUrlAPIView)
# router.register(r'set-with-ratio', SetWithRatioViewSet)
# router.register(r'default-es-query', DefaultESQueryViewSet)
# router.register(r'set-list-es', SiteEnableSetsESViewSet)
router.register(r'get-mapped-property-types', GetMappedPropertyTypeAPIView)
router.register(r'get-sts-config', NewGetSTSConfigViewSetMT)
router.register(r'property-type-refresh', PropertyTypeRefressAPIView)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    # path('get-sts-config/', combined_api_response, name='combined-api'),
    path(
        'redirection-rules/',
        LeaveBehindPopUnderRulesAPIView.as_view(),
        name='redirection-rules'
    ),
    path(
        'amenity-types-refresh/',
        AmenityTypeRefresh.as_view(),
        name='amenity-types-refresh'
    ),
    path(
        'amenity-types-refresh/<int:id>/',
        AmenityTypeUpdateDeleteView.as_view(),
        name='amenity-types-update-delete'
    ),
    path(
        'partner-amenity-type-refresh/',
        PartnerAmenityTypeRefresh.as_view(),
        name='partner-amenity-type-refresh'
    ),
    path(
        'partner-amenity-type-refresh/<int:id>/',
        PartnerAmenityTypeUpdateDeleteView.as_view(),
        name='partner-amenity-type-update-delete'
    ),
]
