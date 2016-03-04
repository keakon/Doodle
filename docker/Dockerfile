FROM ubuntu:14.04
MAINTAINER keakon <keakon@gmail.com>

ENV DOODLE_PATH /data/doodle

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git wget python build-essential python-dev libcurl4-openssl-dev

RUN git clone https://github.com/keakon/Doodle.git $DOODLE_PATH
WORKDIR $DOODLE_PATH
RUN scripts/buildout.sh

ENTRYPOINT ["bin/doodle"]