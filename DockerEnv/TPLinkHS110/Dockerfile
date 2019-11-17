FROM python:2.7-slim
WORKDIR /app
COPY MQTT_TplinkHS110Monitor.py .
COPY requirements.txt .
COPY HS110 ./HS110
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt
EXPOSE 9998/udp

ENV PYTHONPATH=/non-git-local-includes/

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_HS110Monitor"
ENV Client_Name=$buildtime_Client_Name

CMD ["sh", "-c", "python MQTT_TplinkHS110Monitor.py -b ${IP_Brocker} -c ${Client_Name}"]
