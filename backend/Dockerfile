FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["sh", "run.sh"]
LABEL author='d4mir.sh.d@yandex.ru' version=1
