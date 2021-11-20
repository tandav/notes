run:
	uvicorn server:app --host 0.0.0.0 --port 5003 --ssl-certfile fullchain.pem --ssl-keyfile privkey.pem
