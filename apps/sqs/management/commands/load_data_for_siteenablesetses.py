from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sqs.models import SetListES, SiteEnableSetsES
from apps.brands.models import Brand
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/site_enable_sets_es.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                data_dict = {}
                for data_json in data_json_list:
                    active = data_json.get("active")
                    if active:
                        created_at = data_json.pop('create_date')
                        updated_at = data_json.pop('update_date')
                        data_json['created_at'] = created_at
                        data_json['updated_at'] = updated_at
                        
                        set_list_id = int(data_json.pop('set_list_id')) 
                        data_json['set_list'] = set_list_id

                        brand_key = data_json.pop('site')
                        brand = Brand.objects.get(key=brand_key.upper())
                        
                        if set_list_id in data_dict.keys():
                            data_dict[set_list_id]['brands'].append(brand.id)
                        else:
                            data_json['brands'] = [brand.id]
                            data_dict[set_list_id] = data_json
                print(data_dict)
                for k,v in data_dict.items():
                    set_list = SetListES.objects.get(id=v.pop('set_list'))
                    brands = v.pop('brands')
                    es = SiteEnableSetsES.objects.create(
                        set_list=set_list,
                        **v
                    )
                    es.brands.set(brands)

        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brand location partners property data!'))