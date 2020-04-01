FROM python:3.7-slim
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

ENV PYTHONPATH=/non-git-local-includes/
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_Sound"
ENV Client_Name=$buildtime_Client_Name

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY MQTT_Soundcontroller.py .
CMD python MQTT_Soundcontroller.py  -b ${IP_Brocker} -c ${Client_Name}
