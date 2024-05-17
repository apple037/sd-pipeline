import random
import time
from datetime import datetime
from sanic.log import logger

from pymongo import MongoClient

import config
import default
from api import models
from api.models import pipelineJob
from function.txt2img import proceed_txt2img, sd_heartbeat

avatar_category_dict = {}
avatar_lora_dict = {}
ongoing_job_count = 0


# 初始化產圖任務
def init_job(request):
    job = pipelineJob(
        name_list=request.json.get('name_list'),
        prompt_count=request.json.get('prompt_count'),
        count=request.json.get('count'),
        width=request.json.get('width'),
        height=request.json.get('height'),
        to_gcp=request.json.get('to_gcp')
    )
    return job


# 驗證產圖任務
def validate_job(job: pipelineJob):
    if job.name_list is None or len(job.name_list) == 0:
        raise Exception("Name list is empty")
    if job.prompt_count is None or job.prompt_count <= 0:
        raise Exception("Prompt count is invalid")
    if job.count is None or job.count <= 0:
        raise Exception("Count is invalid")
    if job.width is None or job.width <= 0:
        raise Exception("Width is invalid")
    if job.height is None or job.height <= 0:
        raise Exception("Height is invalid")
    if job.to_gcp is None:
        raise Exception("To gcp option is invalid")


# 紀錄任務
def save_job(job: pipelineJob):
    client, db = get_mongo_db_connection()
    collection = db['job']
    # build job dict
    job_dict = job.to_dict()
    job_dict['status'] = 'running'
    # save time yyyy-mm-dd hh:mm:ss
    job_dict['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_dict['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job_dict['progress'] = 0
    # insert job to mongodb
    result = collection.insert_one(job_dict)
    logger.info("Job id: " + str(result.inserted_id))
    client.close()
    global ongoing_job_count
    ongoing_job_count += 1
    return result.inserted_id


# 更新任務進度
def update_job_progress(job_id: str):
    # update job progress by job id
    logger.info("[更新進度][id: " + str(job_id) + "]")
    client, db = get_mongo_db_connection()
    collection = db['job']
    job = collection.find_one({'_id': job_id})

    if job['progress'] + 1 == job['count']:
        job['status'] = 'finished'
        global ongoing_job_count
        ongoing_job_count -= 1
    job['progress'] = job['progress'] + 1
    job['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collection.update_one({'_id': job_id}, {'$set': job})
    client.close()


# 紀錄產圖詳細資訊
def record_to_db(name: str, path: str, prompts: str, negative_prompts: str, used_time: float, job_id: str):
    client, db = get_mongo_db_connection()
    collection = db['auto_generated_image_detail']
    # build detail dict
    detail_dict = {'name': name, 'path': path, 'prompts': prompts, 'negative_prompts': negative_prompts,
                   'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "used_time": used_time, "job_id": job_id}
    collection.insert_one(detail_dict)
    client.close()


# 取得執行中任務
def get_running_jobs():
    client, db = get_mongo_db_connection()
    collection = db['job']
    # find running job
    result = collection.find({'status': 'running'})
    job_list = []
    for job in result:
        job_dist = {'id': str(job['_id']), 'count': job['count'], 'progress': job['progress']}
        job_list.append(job_dist)
    client.close()
    res = {'jobs': job_list}
    return res


# 確認連線
def check_sd_server():
    sd_heartbeat(config.HEARTBEAT_URL)


# 執行任務
def execute_job(request):
    # check stable diffusion server is running
    check_sd_server()
    # build job by request
    job = init_job(request)
    # validate job here
    validate_job(job)
    # save job to mongodb
    job_id = save_job(job)
    get_auto_avatar_config(job.name_list)
    for times in range(job.count):
        # 一個avatar跑一次
        logger.info("============第" + str(times + 1) + "次============")
        for name in job.name_list:
            # 設置計時器
            start = time.time()
            logger.info("-----------------------")
            logger.info("名稱: " + str(name))
            # 每個category都挑 至少一個 至多prompt_count個
            prompts = pick_prompts(name, job.prompt_count)
            logger.info("[選擇提示詞]: " + str(prompts))
            # 添加預設提示詞
            prompts = default.PROMPTS + prompts
            lora_prompt = random_weight(avatar_lora_dict[name])
            logger.info(f'[lora提示詞]: {lora_prompt}')
            prompts = prompts + "," + lora_prompt
            logger.info("[完整提示詞]: " + str(prompts))
            negative_prompt = default.NEG_PROMPTS
            logger.info("[負面提示詞]: " + str(negative_prompt))
            if job.to_gcp:
                output_path = config.GCP_IMAGE_OUTPUT + name + "/" + datetime.now().strftime(
                    "%Y-%m-%d") + "/"
            else:
                output_path = config.IMAGE_OUTPUT + name + "/" + datetime.now().strftime(
                    "%Y-%m-%d") + "/"
            logger.info("[輸出路徑]: " + str(output_path))
            request = models.TextToImageRequest(
                prompt=prompts,
                negative_prompt=negative_prompt,
                width=job.width,
                height=job.height,
                output=output_path
            )
            # 產圖
            image_url = proceed_txt2img(url=config.TXT2IMG_URL, body_data=request, to_gcp=job.to_gcp)
            logger.info("[產圖完成]")
            end_time = time.time()
            logger.info("[單次產圖時間]: " + str(end_time - start))
            # 更新進度
            update_job_progress(job_id)
            # 紀錄產圖細節
            record_to_db(name, image_url, prompts, negative_prompt, end_time - start, job_id)
    success_res = {
        "status": "success",
        "job_id": str(job_id)
    }
    return success_res


# 取得任務所需設定檔
def get_auto_avatar_config(name_list):
    client, db = get_mongo_db_connection()
    collection = db['auto_avatar_config']
    avatars = collection.find({'name': {'$in': name_list}})
    for avatar in avatars:
        # 添加mongo配置檔
        avatar_category_dict[avatar['name']] = avatar['category']
        # 添加mongo lora檔
        avatar_lora_dict[avatar['name']] = avatar['lora']
    client.close()


# 選擇提示詞
def pick_prompts(name, prompt_count):
    client, db = get_mongo_db_connection()
    collection = db['auto_category_prompt']
    result = []
    category_prompts = collection.find({'name': name})
    for category_prompt in category_prompts:
        logger.info(f'[提示詞類別]: {category_prompt["category"]}')
        # 取得各個category的prompt list
        prompts = category_prompt["prompts"]
        # 隨機挑選prompt_count個prompt
        random.shuffle(prompts)
        max_size = prompt_count
        if len(prompts) < max_size:
            max_size = len(prompts)
        picked = prompts[:max_size]
        for prompt in picked:
            logger.info(f'[選擇提示詞]: {prompt}')
        result.extend(picked)
    client.close()
    return ', '.join(result)


def random_weight(lora: str):
    # 驗證lora格式
    if lora is None or lora == "":
        raise Exception("[lora格式錯誤]")
    random_w = random.randint(50, 100) / 100
    replaced = lora.replace("[WEIGHT]", str(random_w))
    if replaced == lora:
        raise Exception("[lora格式錯誤]")
    return replaced


# 取得mongo連線
def get_mongo_db_connection():
    client = MongoClient(config.MONGODB_CONNECTION)
    db = client[config.MONGODB_DB]
    return client, db
