from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponse
from django.views.i18n import set_language
from apps.property.views import DragAndDropPartnerPropertyMappingView
from apps.amenities.views import AmenityTypeMappingView


def health_check(request):
    return HttpResponse('OK', status=200)


admin.site.site_header = "STS Admin Site"
admin.site.site_title = "STS Admin"
admin.site.login_title = "STS Admin Login(test)"

urlpatterns = [
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # path('', TemplateView.as_view(template_name='index.html'), name='home'),
    # path('', RedirectView.as_view(pattern_name='dashboard:index')),
    path('health/', health_check, name='health-check'),
    path('set_language/', set_language, name='set_language'),
    # path('', include('apps.dashboard.urls')),
    # path('brands/', include('apps.brands.urls')),
    # path('sqs/', include('apps.sqs.urls')),
    # path('partners/', include('apps.partners.urls')),
    # path('sts/', include('apps.sts.urls')),
    # path('accounts/', include('apps.accounts.urls')),
    # path('sts/', include('apps.sts.urls')),
    # path('', include('apps.property.urls')),
    # path('amenities/', include('apps.amenities.urls')),
    path('drag-and-drop-partner-property-mapping/', DragAndDropPartnerPropertyMappingView.as_view(),
         name='drag-and-drop-partner-property-mapping'),
    path('amenity-type-mapping/', AmenityTypeMappingView.as_view(), name='amenity-type-mapping'),
    path('', admin.site.urls),
]

