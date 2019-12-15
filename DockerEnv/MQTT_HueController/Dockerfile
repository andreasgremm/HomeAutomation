FROM huemodule:prod
WORKDIR /app
COPY MQTT_HueController.py .
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

ENV PYTHONPATH=/non-git-local-includes/

ARG buildtime_IP_Brocker="192.168.1.237"
ENV IP_Brocker=$buildtime_IP_Brocker

ARG buildtime_Client_Name="MQTT_Hue"
ENV Client_Name=$buildtime_Client_Name

CMD ["sh", "-c", "python MQTT_HueController.py -b ${IP_Brocker} -c ${Client_Name}"]
