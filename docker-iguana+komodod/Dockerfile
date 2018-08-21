FROM ubuntu:16.04

USER root
WORKDIR /

# copy binaries from base docker images
COPY --from=kmdplatform/komodod /komodo/src/komodo-cli /usr/local/bin/komodo-cli
COPY --from=kmdplatform/komodod /komodo/src/komodod /usr/local/bin/komodod
COPY --from=kmdplatform/komodod /home/komodo /home/komodo
COPY --from=kmdplatform/komodod /usr/lib/x86_64-linux-gnu/libcurl-gnutls.so.4 /usr/lib/x86_64-linux-gnu/libcurl-gnutls.so.4
COPY --from=kmdplatform/iguana /SuperNET /SuperNET
COPY --from=kmdplatform/iguana /usr/local/lib/libnanomsg.so.5 /usr/local/lib/libnanomsg.so.5

# link libraries
RUN ldconfig

# install dependency packages
RUN apt update \
    && apt install -y libssl-dev libcurl4-openssl-dev libgomp1 python3-requests redir \
    && rm -rf /var/lib/apt/lists/*

# initialize environment
RUN useradd -u 3003 -M komodo -d /home/komodo \
    && chown -R komodo:komodo /home/komodo
ENV PATH="/SuperNET/iguana:${PATH}"
USER komodo
WORKDIR /home/komodo
ENV HOME=/home/komodo
RUN mkdir /home/komodo/.komodo \
    && touch /home/komodo/.komodo/komodo.conf 

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

