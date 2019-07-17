FROM python:2.7-slim
WORKDIR /app
COPY MQTT_TplinkHS110Monitor.py .
COPY requirements.txt .
COPY HS110 ./HS110
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 9998/udp
ENV PYTHONPATH=/non-git-local-includes/
CMD ["python", "MQTT_TplinkHS110Monitor.py","-b","192.168.1.237","-c","test"]
