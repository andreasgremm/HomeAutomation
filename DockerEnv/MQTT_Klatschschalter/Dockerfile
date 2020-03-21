FROM python:3.8-slim

USER root
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /tmp/requirements.txt

ENV PYTHONPATH=/non-git-local-includes/
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_Klatschschalter"
ENV Client_Name=$buildtime_Client_Name

ARG buildtime_API_Conn="192.168.1.237:81"
ENV API_Conn=$buildtime_API_Conn

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY MQTT_Klatschschalter.py .
# CMD ["sh", "-c", "python MQTT_Motiondetektor.py  -b ${IP_Brocker} -c ${Client_Name}"]
CMD python MQTT_Klatschschalter.py  -b ${IP_Brocker} -c ${Client_Name} -a ${API_Conn}
