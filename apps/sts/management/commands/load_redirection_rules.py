import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sts.service.ratio_set import RatioSetService
from core.service import CoreService
from apps.partners.models import Partner
from apps.sts.models import Location, Device, LeaveBehindPopUnderRules
from apps.property.models import PropertyType


class Command(BaseCommand):
    help = "Load redirection rules"
    core_service = CoreService()
    ratioset_service = RatioSetService()

    # def add_arguments(self, parser):
    #     parser.add_argument('--file', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)
        file = "data/static_data/redirection-rules.json"
        try:
            self.stdout.write('Cloning ratio sets...')
            with open(file, 'r') as fp:
                data = fp.read()
                data_dict = json.loads(data)
                for k, v in data_dict.items():
                    pid, cc, device, pt = k.split('-')
                    try:
                        partner = Partner.objects.filter(feed=pid).first()
                        location = Location.objects.filter(country_code=cc).first()
                        device = Device.objects.get(type__iexact=device)
                        property_type = pt.lower()
                        tiles = Partner.objects.filter(feed=v['tiles-lb']).first()
                        details = Partner.objects.filter(feed=v['details-lb']).first()
                        detailspu = Partner.objects.filter(feed=v['details-pu']).first() if v['details-pu'] else None

                        LeaveBehindPopUnderRules.objects.create(
                            partner=partner,
                            location=location,
                            device=device,
                            property_type=property_type,
                            tiles_lb_partner=tiles,
                            details_lb_partner=details,
                            popunder_partner=detailspu
                        )

                    except Exception as e:
                        print(e)
                        pass

        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e}'))

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")