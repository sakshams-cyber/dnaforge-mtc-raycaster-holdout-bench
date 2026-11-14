FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils && rm -rf /var/lib/apt/lists/*
COPY requirements-source.txt /tmp/requirements-source.txt
RUN pip install --no-cache-dir -r /tmp/requirements-source.txt
WORKDIR /app
COPY workspace/ /app/workspace/
RUN mkdir -p /app/output

COPY source_tool.py /app/source_tool.py

RUN pip freeze > /app/ENVIRONMENT_PACKAGES.txt
