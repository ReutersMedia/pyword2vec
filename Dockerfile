FROM ubuntu:14.04
MAINTAINER kenneth.ellis@thomsonreuters.com

COPY GoogleNews-vectors-negative300.bin.gz /GoogleNews-vectors-negative300.bin.gz

RUN apt-get update && \
    apt-get -y install curl python-pip python-numpy python-scipy nginx supervisor uwsgi uwsgi-plugin-python jq && \
    pip install python-logstash flask gensim 
    
VOLUME /var/log/docker

COPY conf /tmp/conf
COPY src /tmp/src

ENV ENVIRONMENT=dev \
    APPLICATION=word2vec-svr \
    NUM_PYTHON_PROCESSES=1 \
    NUM_UWSGI_THREADS=8 \
    LOG_LEVEL=INFO 

RUN mkdir /run/nginx && \
    cd /tmp/src && \
    python setup.py install --root / && \
    cp /tmp/conf/uwsgi.ini /root/uwsgi.ini && \
    cp /tmp/conf/supervisord.conf /etc/supervisord.conf && \
    cp /tmp/conf/run.sh /root/run.sh && \
    cp /tmp/conf/nginx.conf /etc/nginx/nginx.conf && \
    cp /tmp/conf/uwsgi_params /root/uwsgi_params && \
    addgroup nginx && \
    adduser --system --disabled-password --no-create-home --disabled-login nginx && \
    apt-get clean && \
    rm -rf /tmp/conf && \
    rm -rf /tmp/src 

EXPOSE 80

CMD ["/root/run.sh"]

