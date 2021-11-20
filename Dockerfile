FROM python:3-alpine

RUN pip install fastapi uvicorn python-multipart
COPY *.py /app/
WORKDIR /app

EXPOSE 5003

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5003", "--ssl-certfile", "fullchain.pem", "--ssl-keyfile", "privkey.pem"]
