FROM ubuntu:24.04

# update sources and install dependencies: openssl3.0.13, freeradius3.2.5, vim, net-tools, iproute2 and clean at end
RUN apt update && \
    apt install -y freeradius vim net-tools iproute2 python3 iputils-ping && \
    apt clean && \
    rm -rf /etc/freeradius/3.0/sites-enabled

# copy the freeradius configuration files to /etc/freeradius/3.0
COPY radiusd.conf /etc/freeradius/3.0/radiusd.conf
COPY clients.conf /etc/freeradius/3.0/clients.conf
COPY sites-enable_tls-eap /etc/freeradius/3.0/sites-enabled/tls-eap
COPY sites-enable_peap-eap /etc/freeradius/3.0/sites-enabled/peap-eap
COPY mods-enable_eap /etc/freeradius/3.0/mods-enabled/eap


# copy clients sign py script to /usr/local/bin
COPY sign-client.py /usr/local/bin/sign-client.py

# give the client sign script execution permission
# Info: you can run command `sign-client.py -h` to get help

# use openssl self sign ca key and ca cert, tenyears expiration, 4096 b
# and gen server key and cert, oneyear expiration, 2048 b
# put the files into /etc/freeradius/3.0/certs

# Info: you can self change the subj field to your own info
# but you should remember the server CN, cause you will form server domain name when you do TLS EAP authentication
ARG YOUR_CA_SUBJ='/C=US/ST=CA/L=San Francisco/O=My Company/OU=My Org/CN=My CA'
ARG YOUR_SERVER_SUBJ='/C=US/ST=CA/L=San Francisco/O=My Company/OU=My Org/CN=My Server'



RUN chmod +x /usr/local/bin/sign-client.py  && chown -R freerad:freerad /etc/freeradius/3.0 && \
    openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj "$YOUR_CA_SUBJ" -keyout /etc/freeradius/3.0/certs/ca.key -out /etc/freeradius/3.0/certs/ca.pem && \
    openssl req -new -newkey rsa:2048 -days 365 -nodes -subj "$YOUR_SERVER_SUBJ" -keyout /etc/freeradius/3.0/certs/server.key -out /etc/freeradius/3.0/certs/server.csr && \
    openssl x509 -req -in /etc/freeradius/3.0/certs/server.csr -CA /etc/freeradius/3.0/certs/ca.pem -CAkey /etc/freeradius/3.0/certs/ca.key -CAcreateserial -out /etc/freeradius/3.0/certs/server.pem && \
    chmod +r /etc/freeradius/3.0/certs/server.* 


CMD ["freeradius", "-f"]
# always run for debug
# CMD ["tail", "-f", "/dev/null"]
