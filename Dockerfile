FROM python:3.9-alpine

RUN apk add gcc

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
  && pip install -r requirements.txt \
  && apk del .build-deps gcc musl-dev
COPY src/ .

CMD [ "python", "app.py" ]
