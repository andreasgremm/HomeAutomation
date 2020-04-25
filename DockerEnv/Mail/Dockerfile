FROM python:3.8-slim

ENV PYTHONPATH=/non-git-local-includes/

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

ADD *.py ./Mail/

CMD ["python"]
