from django.urls import path
from .views import BrandsListView, BrandsDetailsView, BrandsUpdateView, BrandsCreateView, BrandSDeleteView


urlpatterns = [
    path('', BrandsListView.as_view(), name='brands-list'),
    path('create/', BrandsCreateView.as_view(), name='brand-add'),
    path('<pk>/', BrandsDetailsView.as_view(), name='brand-detail'),
    path('<pk>/update/', BrandsUpdateView.as_view(), name='brand_update'),
    path('<pk>/delete/', BrandSDeleteView.as_view(), name='brand-delete'),
]
