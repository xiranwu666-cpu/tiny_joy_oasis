FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DB_PATH=/data/app_data.sqlite

RUN mkdir -p /data

COPY . /app

EXPOSE 8000

CMD ["python", "server.py"]
