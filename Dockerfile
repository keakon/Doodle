FROM ubuntu:16.04
RUN apt-get -y update && \
  apt-get install -y --no-install-recommends ca-certificates curl gcc python python-dev libcurl4-openssl-dev libssl-dev
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py
RUN mkdir /root/Doodle
WORKDIR /root/Doodle
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY doodle ./doodle
