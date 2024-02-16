# from celery import shared_task
# from django.core.cache import cache
#
# from apps.brands.models import Brand
# from .services import STSAPIService
#
#
# @shared_task()
# def generate_ratio_api_response_task():
#     api_service = STSAPIService()
#     brands = Brand.objects.all()
#     for brand in brands:
#         site_key = brand.key.upper()
#         response = api_service.get_ratio(site_key)
#         cache.set(site_key, response, timeout=None)
