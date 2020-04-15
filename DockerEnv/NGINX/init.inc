mkdir -p /usr/local/etc/nginx/conf.d
docker run --name tmp-nginx-container -d nginx
docker cp tmp-nginx-container:/etc/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf
docker cp tmp-nginx-container:/etc/nginx/conf.d/default.conf /usr/local/etc/nginx/conf.d/default.conf
docker rm -f tmp-nginx-container
