FROM python:3.9-alpine

RUN apk add gcc

WORKDIR /code

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
  && pip install discord.py \
  && apk del .build-deps gcc musl-dev
COPY src/ .

CMD [ "python", "app.py" ]
