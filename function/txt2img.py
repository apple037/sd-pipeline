import json
import base64
import os
import uuid

import requests
from api import models
from function.google_storage import upload_to_gcs
from sanic.log import logger


def sd_heartbeat(url: str):
    """
    Send a heartbeat to the given URL.
    """
    try:
        res = requests.get(url, timeout=10)
        logger.info("[SD伺服器正常]")
        return res.json()
    except Exception as e:
        logger.error('[SD伺服器異常]: ' + str(e))
        raise Exception('SD伺服器異常')


def proceed_txt2img(url: str, body_data: models.TextToImageRequest, to_gcp: bool):
    """
    Wrap the given URL and body data into a POST request and return the response.
    """
    try:
        logger.info("[產圖開始]")
        res = submit_post(url, body_data)
        image_name = generate_image_name(res)
        base64_image = res.json()['images'][0]
        if to_gcp is False:
            check_output_path(body_data.output)
            save_encoded_image(base64_image, body_data.output + image_name)
            return body_data.output + image_name
        else:
            bucket_name, credentials_file_path = get_bucket_info()
            return upload_to_gcs(bucket_name, base64.b64decode(base64_image), body_data.output + image_name,
                                 credentials_file_path)
    except Exception as e:
        print('Error: ' + str(e))
        return {'error': str(e)}


def submit_post(url: str, body_data: models.TextToImageRequest):
    """
    Submit a POST request to the given URL with the given data.
    """
    check_body(body_data)
    # add_default_values(body_data)
    return requests.post(url, data=json.dumps(body_data.to_json()))


def generate_image_name(res: requests.Response):
    """
    Generate an image name using UUID.
    """
    new_uuid = uuid.uuid4()
    return str(new_uuid) + '.png'


def check_output_path(output_path: str):
    # 檢查資料夾是否存在，並在必要時創建資料夾
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        logger.warn("[資料夾不存在，創建資料夾]")
        os.makedirs(output_dir)
        logger.info("[資料夾創建完成][路徑: " + output_dir + "]")


def save_encoded_image(b64_image: str, output_path: str):
    """
    Save the given image to the given output path.
    """
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(b64_image))


def get_bucket_info():
    return "mygram-ai-backend-bucket", "./resources/mygram-ai-dev.json"


def check_body(body_data: models.TextToImageRequest):
    """
    Check if the given body data is valid.
    """
    if body_data.prompt is None:
        raise ValueError('Missing prompt in body data.')
    if body_data.width is None:
        raise ValueError('Missing width in body data.')
    if body_data.height is None:
        raise ValueError('Missing height in body data.')
    if body_data.output is None:
        raise ValueError('Missing output in body data.')
    else:
        if body_data.output.endswith('/') is False:
            raise ValueError('Output path must end with /')


def add_default_values(body_data: models.TextToImageRequest):
    """
    Add default values to the given body data.
    """
    body_data.prompt = body_data.prompt + ' '


if __name__ == '__main__':
    txt2img_url = 'http://127.0.0.1:7861/sdapi/v1/txt2img'
    data = {'prompt': 'a dog wearing a hat',
            'width': 512, 'height': 512}
    response = submit_post(txt2img_url, data)
    name = generate_image_name(response)
    save_encoded_image(response.json()['images'][0], '../outputs/' + name)
