import datetime
import json
import ast
from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone
from ast import literal_eval
from api import BASE_STS_PATH
from api.services import STSAPIService
from apps.partners.models import Partner
from apps.sts.models import BrandLocationDefinedSetsRatio, DuplicatePropertyPartnerOrder
from apps.sts.service.ratio_set import RatioSetService
from core.service import CoreService
from core.utils import Utils


class Command(BaseCommand):
    help = "Download Predicted ratio data."
    core_service = CoreService()
    ratioset_service = RatioSetService()

    def add_arguments(self, parser):
        parser.add_argument('--orders', type=str, default=None)
        parser.add_argument('--ratiosetids', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)

        orders = eval(options.get('orders'))
        ratiosetids = eval(options.get('ratiosetids'))

        for rid in ratiosetids:
            ratio = BrandLocationDefinedSetsRatio.objects.get(id=rid)
            dups = DuplicatePropertyPartnerOrder.objects.filter(bldsr=ratio)
            dups.delete()
            for order in orders:
                partner = Partner.objects.get(id=order[0])
                try:
                    obj, created = DuplicatePropertyPartnerOrder.objects.update_or_create(
                        bldsr=ratio,
                        partner=partner,
                        order=order[1]
                    )
                except Exception as e:
                    print(e)
                    pass

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")