FROM ubuntu:18.04

LABEL Description="A Docker image for mjpg_streamer." Version="0.4"

RUN apt-get update && apt-get install -y libjpeg8 tzdata
RUN mkdir /mnt/pictures_out

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN useradd mjpegstreamer
WORKDIR /home/mjpegstreamer

COPY docker-start.sh .
RUN chmod 755 docker-start.sh
COPY mjpg_streamer .
ADD *.so ./
ADD www ./www

EXPOSE 8080/TCP

ENTRYPOINT ["/home/mjpegstreamer/docker-start.sh", "output_http.so -n -w ./www -p 8080", "output_file.so -d 5000 -f /mnt/pictures_out"]

CMD ["input_uvc.so -d /dev/video0"]
