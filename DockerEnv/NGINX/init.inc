cp logrotate.conf /etc/logrotate.d/nginx
mkdir -p /usr/local/etc/nginx/conf.d
mkdir -p /var/log/nginx
docker run --name tmp-nginx-container -d nginx
docker cp tmp-nginx-container:/etc/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf
docker cp tmp-nginx-container:/etc/nginx/conf.d/default.conf /usr/local/etc/nginx/conf.d/default.conf
docker rm -f tmp-nginx-container
