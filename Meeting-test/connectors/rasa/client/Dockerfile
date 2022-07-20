FROM alpine:3.15

# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1

#RUN apk add --no-cache python2 && \
 #  python -m ensurepip && \
  # rm -r /usr/lib/python*/ensurepip && \
   #pip install --upgrade pip setuptools && \
   #rm -r /root/.cache


#FROM alpine:3.11

# VERSIONS
#ENV ALPINE_VERSION=3.11 \
 #   PYTHON_VERSION=2.7.16

# PATHS
#ENV PYTHON_PATH=/usr/local/bin/ \
    #PATH="/usr/local/lib/python$PYTHON_VERSION/bin/:/usr/local/lib/pyenv/versions/$PYTHON_VERSION/bin:${PATH}" \

#RUN apk update && apk upgrade && apk add python3
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN python --version
RUN apk add --no-cache --virtual .build-deps curl sed python3 make g++
RUN apk update && apk add nodejs
RUN apk add --update npm
WORKDIR /app/
RUN curl -L -o rvi.zip "https://github.com/RasaHQ/rasa-voice-interface/archive/master.zip" && unzip rvi.zip && rm rvi.zip
WORKDIR /app/rasa-voice-interface-master
RUN npm install -g node-gyp
RUN npm install -g npm

RUN chown -R root /app/rasa-voice-interface-master \
  && sed -i "s|'http://localhost:5005'|'${RASA_ENDPOINT}', options: { path: '${RASA_PATH}' }|g" src/main.js \
  && sed -i "s|integrity: false|integrity: false, publicPath: '${PUBLIC_PATH}'|g" vue.config.js \
  && npm install --no-optional && npm install serve
RUN apk del .build-deps

EXPOSE 8080
USER node
CMD PORT=8080 npx serve -s dist

