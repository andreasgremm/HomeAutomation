


https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/


https://github.com/softScheck/tplink-smartplug

Clone:
https://github.com/andreasgremm/HomeAutomation.git


docker volume create non-git-local-includes

docker volume ls
DRIVER              VOLUME NAME
local               non-git-local-includes


Small lightweight container to manage volumes:
Dockerfile:
FROM scratch
CMD

docker build -t nothing .
docker container create --name temp --mount source=non-git-local-includes,destination=/non-git-local-includes nothing

Alternative2:
docker container create --name temp --mount source=non-git-local-includes,destination=/non-git-local-includes busybox

Copy to Volume:
docker cp Security temp:/non-git-local-includes/Security/

Copy from Volume:
docker cp temp:/non-git-local-includes/Security/ <some Directory>

Test:
docker run --rm -it --mount source=non-git-local-includes,destination=/non-git-local-includes busybox

docker rm temp



docker build --tag=tplinkmonitor .

docker run -d \
  --name=tplinkmonitor \
  --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
   --restart unless-stopped \
  tplinkmonitor:latest



