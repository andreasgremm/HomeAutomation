FROM alpine:latest
RUN apk add --no-cache ffmpeg
RUN apk add --no-cache bash
RUN apk add tzdata

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /mnt/pictures_input
RUN mkdir /mnt/video_output

RUN addgroup -S appgroup && adduser -S appuser -G appgroup -D -h /home/appuser
WORKDIR /home/appuser
USER appuser
ADD pictures2video.bash .

ENTRYPOINT ["/home/appuser/pictures2video.bash"]
CMD ["/mnt/pictures_input", "/mnt/video_output", "pictures2video"]
