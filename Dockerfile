# Base image with python dependencies
FROM python:3.10-slim-bullseye as base
RUN apt-get update && \
    apt-get -y install \
        git
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Fetch node modules
FROM node:latest as node
COPY package.json /package.json
RUN npm install

# Build staticfiles
FROM base as staticfiles
COPY bookmarks /app
COPY --from=node /node_modules /node_modules
RUN python /app/manage.py collectstatic --noinput

# Runtime image
FROM base
ENV SQLITE_DATABASE_PATH=/data/db.sqlite3
COPY --from=staticfiles /app /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir /data
EXPOSE 8000
CMD ["/entrypoint.sh"]