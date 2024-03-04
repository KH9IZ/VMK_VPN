FROM ghcr.io/xtls/xray-core:latest

COPY configs.d/* /etc/xray/conf.d/
RUN rm /etc/xray/config.json

ENV TZ=Europe/Berlin
RUN /usr/bin/xray run -test -confdir /etc/xray/conf.d
ENTRYPOINT [ "/usr/bin/xray" ]
CMD [ "-confdir", "/etc/xray/conf.d" ]
