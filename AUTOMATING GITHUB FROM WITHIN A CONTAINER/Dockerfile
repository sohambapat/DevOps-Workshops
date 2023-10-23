# 2023 DEVOPS - CSC 519 - jwore@ncsu.edu
FROM alpine:latest

COPY github_branch_create.py /home
USER root
WORKDIR /home

RUN apk --update-cache add python3
RUN apk --no-cache add py3-requests

#CMD ["/bin/sh"]
CMD python /home/github_branch_create.py
