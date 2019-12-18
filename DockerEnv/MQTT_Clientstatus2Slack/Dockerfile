FROM python:3.7-slim
WORKDIR /app
COPY MQTT_Clientstatus2Slack.py .
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

ENV PYTHONPATH=/non-git-local-includes/

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_SystemMonitor"
ENV Client_Name=$buildtime_Client_Name

CMD ["sh", "-c", "python MQTT_Clientstatus2Slack.py  -b ${IP_Brocker} -c ${Client_Name}"]
