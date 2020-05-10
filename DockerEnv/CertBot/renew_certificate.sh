  docker-compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
      --email <email>  \
      -d <example.com> \
      --rsa-key-size 4096 \
      --agree-tos \
      --force-renewal" certbot
