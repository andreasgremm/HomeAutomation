FROM python:2.7-slim
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

ENV PYTHONPATH=/non-git-local-includes/
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG buildtime_IP_Brocker="192.168.2.5"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_HS110Monitor"
ENV Client_Name=$buildtime_Client_Name

EXPOSE 9998/udp

WORKDIR /app
ADD HS110 HS110
COPY MQTT_TplinkHS110Monitor.py .

CMD python MQTT_TplinkHS110Monitor.py -b ${IP_Brocker} -c ${Client_Name}
