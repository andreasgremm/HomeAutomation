FROM python:3.8-slim
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ADD *.py ./Hue/

CMD ["python"]
