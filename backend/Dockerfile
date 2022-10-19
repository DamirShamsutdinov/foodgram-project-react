FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["sh", "run.sh"]
