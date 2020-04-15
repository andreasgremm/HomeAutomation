docker run --name nginx \
   --restart unless-stopped \
   --network host \
   -p 80:80 \
   -v /usr/local/etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
   -v /usr/local/etc/nginx/conf.d:/etc/nginx/conf.d:ro \
   -d nginx
