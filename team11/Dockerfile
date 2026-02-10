FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY tripPlanService/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY tripPlanService/ /app/

EXPOSE 50051

CMD ["bash", "-c", "\
python manage.py migrate && \
python presentation/grpc/server/grpc_server.py & \
python -m http.server 2022 & \
python manage.py runserver 0.0.0.0:2004 & \
wait \
"]
