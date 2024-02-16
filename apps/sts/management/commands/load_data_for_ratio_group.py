from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sts.models import RatioLocation, RatioGroup, PartnerRatio, RatioSet
from apps.partners.models import Partner
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/ratio_group.json'

    def populate_data(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for data_json in data_json_list:
                        ratio_group_id = data_json['id']
                        short_name = data_json['short_name']
                        updated_at = data_json['last_modified']
                        archived = data_json['archived']
                        click_weight_ratio = data_json['click_weight_ratio']
                        click_ratio_tiles_plan = data_json['click_ratio_tiles_plan']

                        ratio_set = data_json['ratio_set']
                        partner_ratio_list = [v.strip() for v in ratio_set.split(',')]
                        ratio_list = []
                        while partner_ratio_list:
                            ptr = partner_ratio_list.pop()
                            pt, rt = [v.strip() for v in ptr.split('=')]
                            if int(rt[:-1]) > 0:
                                ratio_list.append(f"{pt}_{rt}")

                        rs_title = ' '.join(ratio_list)

                        rs = RatioSet.objects.create(title=rs_title)
                        for partner_ratio in ratio_list:
                            partner_key, ratio = [v.strip() for v in partner_ratio.split('_')]
                            partner = Partner.objects.filter(key=partner_key)[0]
                            pr, created = PartnerRatio.objects.get_or_create(
                                partner=partner,
                                ratio=int(ratio[:-1]),
                                ratioset=rs
                            )

                        rg = RatioGroup.objects.create(
                            id=ratio_group_id,
                            updated_at=updated_at,
                            ratio_set=rs,
                            short_name=short_name,
                            archived=archived,
                            click_weight_ratio=click_weight_ratio,
                            click_ratio_tiles_plan=click_ratio_tiles_plan
                        )
                        rs.save()
                        print(f"Ratio Set {rs.title} is added!")
                self.stdout.write(self.style.SUCCESS('Successfully loaded location ratio data!'))
            except Exception as e:
                print(f"{e}")
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        self.populate_data()
