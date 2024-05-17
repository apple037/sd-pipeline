from sanic import Sanic
from sanic.response import text, json
from sanic.log import logger

import pipeline

app = Sanic("AutoPainterApi")
app.update_config("./config.py")


@app.get('/hb')
async def heartbeat(request):
    return text("Heartbeat OK")


@app.post("/txt2img")
async def call_txt2img(request):
    return json(pipeline.execute_job(request))


@app.get("/running")
async def running(request):
    return json(pipeline.get_running_jobs())


@app.middleware('request')
async def print_on_request(request):
    # 印出request的參數資訊
    logger.info(f"[請求類型][{request.method}][請求url][{request.url}]")
    # Get 方法印args, Post 方法印body
    if request.method == "POST":
        logger.info(f"[請求Body]: {request.json}")
    else:
        logger.info(f"[請求參數]: {request.args}")


@app.middleware('response')
async def print_on_response(request, response):
    # 印出response的資訊
    logger.info(f"[回應狀態碼][{response.status}][回應內容][{response.body}]")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9008, workers=2)
