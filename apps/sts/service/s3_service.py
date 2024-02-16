from core.service import CoreService


class S3Services:
    core_service = CoreService()

    def s3_file_process(self, bucket_name, local_file_location, s3_object_name, s3_client):
        # delete existing file before update from s3
        try:
            self.core_service.delete_file_from_s3(
                bucket_name=bucket_name, file_key=s3_object_name, s3_client=s3_client
            )
        except Exception as err:
            print(f'S3 file delete error: {err}')
        try:
            self.core_service.upload_file_to_s3(
                local_file_path=local_file_location, bucket_name=bucket_name, s3_object_name=s3_object_name,
                s3_client=s3_client
            )
        except Exception as err:
            print(f'S3 file upload error: {err}')


