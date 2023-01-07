FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential default-libmysqlclient-dev \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /main_app

COPY ./requirements.txt /main_app

RUN pip install --no-cache-dir --requirement /main_app/requirements.txt

COPY . /main_app

EXPOSE 5000

CMD ["python", "server.py"]