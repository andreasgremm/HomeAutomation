FROM alpine:latest

RUN apk -U upgrade

RUN apk --no-cache add tzdata
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apk add --no-cache ttf-liberation
RUN apk add --no-cache imagemagick
RUN apk add --no-cache bash
RUN rm /var/cache/apk/*
RUN chmod 777 /var/cache/fontconfig

RUN mkdir /mnt/camera_input
RUN mkdir /mnt/reduced_output

RUN addgroup -S appgroup && adduser -S appuser -G appgroup -D -h /home/appuser
WORKDIR /home/appuser
USER appuser
ADD Image_diff.bash .

ENTRYPOINT ["/home/appuser/Image_diff.bash"]
CMD ["/mnt/camera_input", "/mnt/reduced_output"]
