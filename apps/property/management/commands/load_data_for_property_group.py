from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.property.models import PropertyGroup
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/accommodation_type.json'

    def populate_data(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for i, data_json in enumerate(data_json_list):
                        data_json.pop('property_category')
                        data_json['property_ordering'] = i
                        pg = PropertyGroup.objects.create(**data_json)
                        print(f"PropertyGroup {pg.name} is created!")
                self.stdout.write(self.style.SUCCESS('Successfully loaded partners data!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
