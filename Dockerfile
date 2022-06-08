FROM python:3.6.15-bullseye

RUN apt update

RUN apt install -y git

RUN mkdir -p /usr/api

COPY . /usr/api

WORKDIR /usr/api

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN wandb login 0f67acb5170832a98b80da3cf33a8a2b8d935898

CMD uvicorn api:api --port :$PORT --host 0.0.0.0
