FROM python:3.11-slim-bullseye
RUN echo "" > /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/debian buster main" >> /etc/apt/sources.list ;
RUN echo "deb http://mirrors.aliyun.com/debian-security buster/updates main" >> /etc/apt/sources.list ;
RUN echo "deb http://mirrors.aliyun.com/debian buster-updates main" >> /etc/apt/sources.list;
# Install GEOS library and clean up in one step
RUN apt-get update && apt-get install -y libgeos-dev pandoc && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

WORKDIR /code

# Copy just the requirements first
COPY ./requirements.txt .
ENV TZ Asia/Shanghai
# Increase timeout might not be necessary but is retained as in original
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt --timeout 100

# Copy the rest of the application
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050", "--env-file", ".env", "--workers", "2", "--log-config", "log.yaml"]