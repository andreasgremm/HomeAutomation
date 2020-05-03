docker run --name nginx \
   --restart unless-stopped \
   --network host \
   -p 80:80 \
   -v /var/log/nginx:/var/log/nginx \
   -v /usr/local/etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
   -v /usr/local/etc/nginx/conf.d:/etc/nginx/conf.d:ro \
   -v /etc/localtime:/etc/localtime:ro \
   -v /etc/timezone:/etc/timezone:ro \
   -d nginx
