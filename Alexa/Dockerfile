FROM python:3.8-alpine
RUN apk update && apk add libressl-dev libffi-dev gcc musl-dev python3-dev
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt
RUN pip install uwsgi
RUN pip install pip==9.0.3
RUN pip install Flask-Ask

ENV PYTHONPATH=/non-git-local-includes/
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN adduser -S appuser
WORKDIR /home/appuser
USER appuser

COPY server-conf/uwsgi.ini /etc/uwsgi/
COPY src src
EXPOSE 3031

CMD /usr/local/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini --die-on-term
