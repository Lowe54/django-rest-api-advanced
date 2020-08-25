FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
# Copy the requirements.txt file
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
# Run the pip command to install the requirements
RUN pip install -r requirements.txt

RUN apk del .tmp-build-deps
# Create app directory
RUN mkdir /app
# Set the work directory
WORKDIR /app
# Copy the app folder from local machine to folder in the docker image
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
# Add the user, -D means applications only, username
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
# Set the user to be used
USER user

