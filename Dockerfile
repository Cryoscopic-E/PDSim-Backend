FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1


EXPOSE 5556

ENTRYPOINT ["python", "src/main.py", "--host", "0.0.0.0"]

