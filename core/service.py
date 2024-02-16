import boto3
from decouple import config as env_config
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError


class CoreService:

    @staticmethod
    def bulk_insert(model, obj_list: list, ignore_conflicts: bool = False):
        try:
            qs = model.objects
            if ignore_conflicts:
                return qs.bulk_create(obj_list, ignore_conflicts=ignore_conflicts, batch_size=20)
            else:
                return qs.bulk_create(obj_list, batch_size=20)
        except Exception as error:
            objs = []
            for obj in obj_list:
                try:
                    obj.save()
                    objs.append(obj)
                except Exception as error:
                    continue

            return objs

    """ S3 process area """

    @staticmethod
    def s3_config():
        return {
            'DEBUG': env_config('DEBUG', default=False, cast=bool),
            'S3_ACCESS_KEY': env_config('S3_ACCESS_KEY'),
            'S3_SECRET_ACCESS_KEY': env_config('S3_SECRET_ACCESS_KEY'),
            'S3_REGION_NAME': env_config('S3_REGION_NAME')
        }

    @staticmethod
    def s3_connection(config: dict):
        try:
            if not config.get('DEBUG'):
                s3 = boto3.client('s3', region_name=config.get("S3_REGION_NAME"))
            else:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=config.get("S3_ACCESS_KEY"),
                    aws_secret_access_key=config.get("S3_SECRET_ACCESS_KEY"),
                    region_name=config.get("S3_REGION_NAME")
                )
            return s3
        except ClientError as e:
            return None

    @staticmethod
    def create_s3_bucket(bucket_name: str, s3_client, region: str = 'us-east-1'):
        try:
            if region is None:
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
            return True
        except ClientError as e:
            print(e)
            return False

    @staticmethod
    def upload_file_to_s3(local_file_path: str, bucket_name: str, s3_object_name: str, s3_client):
        try:
            # Upload the file
            s3_client.upload_file(local_file_path, bucket_name, s3_object_name, ExtraArgs={'ContentType': 'application/json'})
            print(f"File uploaded successfully to {bucket_name}/{s3_object_name}")
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False

    @staticmethod
    def check_file_exists_in_s3(bucket_name: str, s3_file_key: str, s3_client):
        try:
            # Head object to check if the file exists
            s3_client.head_object(Bucket=bucket_name, Key=s3_file_key)
            print(f"File '{s3_file_key}' exists in bucket '{bucket_name}'")
            return True
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File '{s3_file_key}' does not exist in bucket '{bucket_name}'")
                return False
            else:
                print(f"Error checking file existence: {e}")
                return False
        except (NoCredentialsError, PartialCredentialsError):
            print("Credentials not available")
            return False

    @staticmethod
    def delete_file_from_s3(bucket_name: str, file_key: str, s3_client):
        # AWS credentials (replace with your own)
        try:
            # Delete the file
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            print(f"File '{file_key}' deleted successfully from bucket '{bucket_name}'")
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False

    @staticmethod
    def create_presigned_url(s3_client, bucket_name: str, object_name: str, expiration: int = 3600):
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(e)
            return None

    @staticmethod
    def download_file_from_s3(bucket_name: str, file_key: str, local_path: str, s3_client):
        try:
            # Download the file from S3
            s3_client.download_file(bucket_name, file_key, local_path)
            print(f"File downloaded successfully: {local_path}")
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False

    """ S3 process end """
