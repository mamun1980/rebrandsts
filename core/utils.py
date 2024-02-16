import concurrent.futures
import errno
import glob
import json
import os
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from simple_history.utils import bulk_create_with_history, bulk_update_with_history
from apps.sts.models import BrandLocationDefinedSetsRatio
from apps.partners.models import Partner


class Utils:

    @staticmethod
    def get_filtered_by_12_partners():
        # feeds = Partner.objects.exclude(feed=12)
        # vrbo = Partner.objects.get(key='VRBO')
        # unique_feeds = [f.id for f in feeds]
        # unique_feeds.append(vrbo.id)
        # partners = Partner.objects.filter(id__in=unique_feeds)
        partners = Partner.objects.all()
        return partners

    @staticmethod
    def paginate_by_chunk_size_or_page_number(data, chunk_size: int = 10, page_number: int = 1):
        paginator = Paginator(data, chunk_size)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return paginator, page, page.object_list, page.has_other_pages()

    def process_brand_location(user, brand, bl_ratio_set):
        try:
            bl_rs = BrandLocationDefinedSetsRatio.objects.get(
                brand=brand,
                location=bl_ratio_set.location,
                search_location=bl_ratio_set.search_location,
                device=bl_ratio_set.device,
                property_group=bl_ratio_set.property_group
            )
            bl_rs.ratio_set = bl_ratio_set.ratio_set
            bl_rs.ratio_set_title = bl_rs.ratio_set_short_title
            bl_rs.updated_at = timezone.now()
            return bl_rs
        except BrandLocationDefinedSetsRatio.DoesNotExist:
            return BrandLocationDefinedSetsRatio(
                brand=brand,
                location=bl_ratio_set.location,
                search_location=bl_ratio_set.search_location,
                device=bl_ratio_set.device,
                property_group=bl_ratio_set.property_group,
                ratio_set=bl_ratio_set.ratio_set,
                ratio_set_title=bl_ratio_set.ratio_set_short_title,

                brand_name=brand.name,
                property_group_name=bl_ratio_set.property_group.name,
                location_name=f"{bl_ratio_set.location.country} ({bl_ratio_set.location.country_code})",
                search_location_name=bl_ratio_set.search_location.search_location,
                device_name=bl_ratio_set.device.type,

                created_by=user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

    @staticmethod
    def process_brand_locations(user, brand, ratio_set_list):
        new_ratio_sets = []
        update_ratio_sets = []
        tuple_dict = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for bl_ratio_set in ratio_set_list:
                ratio_tuple = (
                brand.id, bl_ratio_set.location.id, bl_ratio_set.search_location.id, bl_ratio_set.device.id,
                bl_ratio_set.property_group.id)
                if ratio_tuple not in tuple_dict:
                    tuple_dict[ratio_tuple] = 1
                    futures.append(executor.submit(Utils.process_brand_location, user, brand, bl_ratio_set))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if isinstance(result, BrandLocationDefinedSetsRatio) and result.id is None:
                    new_ratio_sets.append(result)
                else:
                    update_ratio_sets.append(result)

        try:
            # BrandLocationDefinedSetsRatio.objects.bulk_create(new_ratio_sets)
            for rs in new_ratio_sets:
                rs._change_reason = f"Ratio set clone by {user} at {timezone.now()}"
                rs._history_user = user
                rs._history_date = timezone.now()
            bulk_create_with_history(new_ratio_sets, BrandLocationDefinedSetsRatio, batch_size=500)
        except Exception as e:
            print(e)
            pass

        try:
            # BrandLocationDefinedSetsRatio.objects.bulk_update(update_ratio_sets, ['ratio_set', 'ratio_set_title', 'updated_at'])
            for rs in update_ratio_sets:
                rs._change_reason = f"Ratio set created by {user} at {timezone.now()}"
                rs._history_user = user
                rs._history_date = timezone.now()
            bulk_update_with_history(update_ratio_sets, BrandLocationDefinedSetsRatio,
                                     ['ratio_set', 'ratio_set_title', 'updated_at'], batch_size=500)
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def write_json_file(data, file_location):
        try:
            with open(file_location, "w", encoding="utf-8") as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                return True
        except Exception as fnf_error:
            print(fnf_error)
            return False

    @staticmethod
    def read_json_file(file_location):
        body = {}
        try:
            if os.path.exists(file_location):
                with open(file_location) as f:
                    body = json.load(f)
        except FileNotFoundError as fnf_error:
            print(fnf_error)
        return body

    @staticmethod
    def check_file_exists(file_location):
        if os.path.exists(file_location):
            return True
        return False

    @staticmethod
    def remove_files(dir_path, files):
        stats_dir = os.path.join(os.getcwd(), dir_path)
        file_list = glob.glob(os.path.join(stats_dir, files))
        for f in file_list:
            os.remove(f)

    @staticmethod
    def make_dir(dir_path):
        try:
            if os.path.isfile(dir_path):
                os.remove(dir_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            if os.path.isfile(dir_path):
                os.remove(dir_path)
                os.makedirs(dir_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
        except Exception as error:
            print(error)

    @staticmethod
    def seconds_to_days_hours_minutes(seconds):
        # days, remainder = divmod(seconds, 86400)  # 86400 seconds in a day
        hours, remainder = divmod(seconds, 3600)  # 3600 seconds in an hour
        minutes, seconds = divmod(remainder, 60)

        return hours, minutes, seconds

    @staticmethod
    def get_time_difference(old_time, current_time):
        if not old_time:
            return 0
        datetime_object = datetime.strptime(old_time, '%Y-%m-%d %H:%M:%S')
        time_difference = current_time - datetime_object
        minutes_difference = time_difference.total_seconds() / 60
        hours_difference = minutes_difference / 60
        if hours_difference > 23:
            return str(int(minutes_difference / (60 * 24))) + ' days ago'
        elif minutes_difference > 59:
            return str(round(minutes_difference / 60, 2)) + ' Hours ago'
        else:
            return str(int(minutes_difference)) + ' Minutes ago'
