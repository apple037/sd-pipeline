FROM python:3.10-alpine
WORKDIR /sanic
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 9008
CMD ["python", "server.py"]
