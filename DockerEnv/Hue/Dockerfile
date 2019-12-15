FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
ADD *.py ./Hue/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

CMD ["python"]
