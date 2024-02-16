from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.partners.models import Partner, Provider, PartnerProvider
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/kayak_providers.json'

    def populate_brands(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    partner = Partner.objects.get(key='KY')

                    for data_json in data_json_list:
                        date = data_json.pop('date')
                        if date:
                            naive_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                            aware_datetime = timezone.make_aware(naive_datetime, timezone.get_default_timezone())
                            data_json['date'] = aware_datetime
                        else:
                            data_json['date'] = timezone.now()

                        provider_id = data_json['provider_id']
                        name = data_json['provider']

                        provider, created = Provider.objects.get_or_create(
                            name=name,
                            provider_id=provider_id
                        )
                        PartnerProvider.objects.create(
                            partner=partner,
                            provider=provider,
                            order=data_json['provider_order'],
                            date=data_json['date'],
                            is_active=True
                        )

                self.stdout.write(self.style.SUCCESS('Successfully loaded partners data!'))
            except Exception as e:
                print(f"{e}")
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_brands()
