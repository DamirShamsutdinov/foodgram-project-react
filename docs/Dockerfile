FROM python:3.7-slim
WORKDIR /docs
COPY . .
CMD rm Dockerfile && cp -r ../docs ../docs_copy && chmod 755 -R ../docs_copy
