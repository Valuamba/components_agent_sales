FROM python:3.12-alpine AS requirements-cache
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN addgroup -g 101 app && \
    adduser -u 101 -G app -s /bin/sh -D app

# Separate the update from install commands to improve layer caching
RUN apk update && apk upgrade --no-cache

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-libs postgresql-dev \
    icu-dev \
    gettext \
    gettext-dev libpq-dev postgresql postgresql-contrib

WORKDIR /crm

COPY --chown=app:app . .
RUN chmod 777 /crm
RUN chmod 777 /crm/db.sqlite3


# run container as new non-root user
USER app

# update PATH environment variable
ENV PATH=/home/app/.local/bin:$PATH

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]