docker run -d \
   --name=uwsgi \
   --network host \
   --mount non-git-local-includes,destination=/non-git-local-includes,readonly \
   --restart unless-stopped \
    uwsgi:prod
