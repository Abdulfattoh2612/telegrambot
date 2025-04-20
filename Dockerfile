FROM php:8.1-cli

COPY . /usr/src/myapp
WORKDIR /usr/src/myapp

CMD [ "php", "-S", "0.0.0.0:10000" ]
