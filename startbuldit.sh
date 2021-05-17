#!/usr/bin/env bash 

docker run --name bludit \
    -p 8080:80 \
    -d bludit/docker:latest 2>/dev/null

if [ $? -ne 0 ];then
docker start bludit
fi