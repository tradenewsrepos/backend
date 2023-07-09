# pull official base image
FROM python:3.8-slim-buster


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code"

ARG SECRET_KEY
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_DB

# Основные зависимости
RUN apt update && apt install -y gcc

# Установим питоньи зависимости
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt \
#
# Cleanup unnecessary stuff
&& apt-get purge -y  \
                -o APT::AutoRemove::RecommendsImportant=false \
&& rm -rf /var/lib/apt/lists/* \
        /tmp/*

# copy project
COPY . .
RUN echo $POSTGRES_DB
RUN echo $POSTGRES_HOST
RUN #python manage.py loaddata fixtures.json

CMD [ "gunicorn", "--workers=2", "--threads=100", "--access-logfile=-", \
    "--error-logfile=-", "--bind=0.0.0.0:8888", "newsfeedner_project.wsgi:application" \
]
