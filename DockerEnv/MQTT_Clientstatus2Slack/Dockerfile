FROM python:3.7-slim
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

ENV PYTHONPATH=/non-git-local-includes/

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_SystemMonitor"
ENV Client_Name=$buildtime_Client_Name

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY MQTT_Clientstatus2Slack.py .
CMD ["sh", "-c", "python MQTT_Clientstatus2Slack.py  -b ${IP_Brocker} -c ${Client_Name}"]
