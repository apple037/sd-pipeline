from google.cloud import storage
from google.oauth2 import service_account
from sanic.log import logger


def upload_to_gcs(bucket_name, image_bytes, destination_blob_name, credentials_file_path):
    logger.info("[上傳圖片至GCP]")
    logger.info("[Bucket名稱: " + bucket_name + "]")
    logger.info("[目標位置: " + destination_blob_name + "]")
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image_bytes, content_type='image/png')
    return blob.public_url
