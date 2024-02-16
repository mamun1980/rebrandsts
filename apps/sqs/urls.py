from django.urls import path
from .views import SetListESListView, SetListESListDetailView, SetListESListUpdateView, SetListESListDeleteView, SetListESListCreateView, \
SiteEnableSetsESListView, SiteEnableSetsESDetailView, SiteEnableSetsESUpdateView, SiteEnableSetsESDeleteView, SiteEnableSetsESCreateView

app_name = "sqs"

urlpatterns = [
    path('set-list-es/', SetListESListView.as_view(), name='set-list-es-list'),
    path('set-list-es/create/', SetListESListCreateView.as_view(), name='set-list-es-create'),
    path('set-list-es/<pk>/', SetListESListDetailView.as_view(), name='set-list-es-detail'),
    path('set-list-es/<pk>/update/', SetListESListUpdateView.as_view(), name='set-list-es-update'),
    path('set-list-es/<pk>/delete/', SetListESListDeleteView.as_view(), name='set-list-es-delete'),
    # path('create/', PartnerCreateView.as_view(), name='partners-add'),
    # path('<pk>/', PartnerDetailsView.as_view(), name='partners-detail'),
    # path('<pk>/update', PartnerUpdateView.as_view(), name='partners_update'),
    # path('<pk>/delete/', PartnerDeleteView.as_view(), name='partners-delete'),

    path('site-enable-set-es/', SiteEnableSetsESListView.as_view(), name='site-enable-set-es-list'),
    path('site-enable-set-es/create/', SiteEnableSetsESCreateView.as_view(), name='site-enable-set-es-create'),
    path('site-enable-set-es/<pk>/', SiteEnableSetsESDetailView.as_view(), name='site-enable-set-es-detail'),
    path('site-enable-set-es/<pk>/update/', SiteEnableSetsESUpdateView.as_view(), name='site-enable-set-es-update'),
    path('site-enable-set-es/<pk>/delete/', SiteEnableSetsESDeleteView.as_view(), name='site-enable-set-es-delete'),
]