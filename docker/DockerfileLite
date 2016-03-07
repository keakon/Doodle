FROM alpine:3.3
MAINTAINER keakon <keakon@gmail.com>

ENV DOODLE_PATH /data/doodle

RUN apk update &&
	apk add --no-cache \
		git \
		wget \
		gcc \
		python \
		python-dev \
		musl-dev \
		curl-dev && \
	rm -rf /var/cache/*

RUN git clone https://github.com/keakon/Doodle.git $DOODLE_PATH
WORKDIR $DOODLE_PATH
ADD https://api.github.com/repos/keakon/Doodle/commits /tmp/commits
RUN git fetch && git reset --hard origin/master
RUN if [ ! -f bin/buildout ]; then \
	mkdir downloads -p; \
	wget https://bootstrap.pypa.io/bootstrap-buildout.py -O bootstrap-buildout.py && python bootstrap-buildout.py --setuptools-to-dir downloads; \
fi
RUN bin/buildout -N

RUN apk del git wget gcc python-dev musl-dev
RUN rm -rf /var/cache/* /tmp/*

ENTRYPOINT ["bin/doodle"]