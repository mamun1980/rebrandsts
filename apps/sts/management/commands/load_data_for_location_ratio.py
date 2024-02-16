from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sts.models import RatioLocation
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/location_ratio.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:

                    id = data_json['id']
                    location_name = data_json['ratio_set']
                    updated_at = data_json['last_modified']
                    rl = RatioLocation.objects.create(
                        id=id,
                        location_name=location_name,
                        updated_at=updated_at
                    )
                    print(f"Ratio Location is added {rl.location_name}")
            self.stdout.write(self.style.SUCCESS('Successfully loaded location ratio data!'))

        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        self.populate_data()
