FROM ubuntu:14.04
MAINTAINER keakon <keakon@gmail.com>

ENV DOODLE_PATH /data/doodle

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git wget python build-essential python-dev libcurl4-openssl-dev

RUN git clone https://github.com/keakon/Doodle.git $DOODLE_PATH
WORKDIR $DOODLE_PATH
ADD https://api.github.com/repos/keakon/Doodle/commits /tmp/commits
RUN git fetch && git reset --hard origin/master
RUN scripts/buildout.sh

RUN apt-get purge --auto-remove -y git wget build-essential python-dev
RUN apt-get clean autoclean && apt-get autoremove -y
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["bin/doodle"]