FROM ubuntu:14.04
MAINTAINER keakon <keakon@gmail.com>

ENV DOODLE_PATH /data/doodle

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git wget python build-essential python-dev libcurl4-openssl-dev

RUN git clone https://github.com/keakon/Doodle.git $DOODLE_PATH
WORKDIR $DOODLE_PATH
ADD https://api.github.com/repos/keakon/Doodle/commits /tmp/commits
RUN git fetch && git reset --hard origin/master
ADD https://raw.githubusercontent.com/keakon/Doodle/master/buildout.cfg /tmp/buildout.cfg
ADD https://raw.githubusercontent.com/keakon/Doodle/master/setup.py /tmp/setup.py
RUN scripts/buildout.sh

RUN apt-get purge -y git wget build-essential python-dev libcurl4-openssl-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["bin/doodle"]