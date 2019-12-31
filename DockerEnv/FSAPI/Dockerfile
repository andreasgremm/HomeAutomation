FROM python:3.8-slim
RUN apt-get update && apt-get install -y  gcc libxslt1-dev libxml2-dev zlib1g-dev && apt-get clean

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ADD *.py ./FSAPI/

CMD ["python"]
