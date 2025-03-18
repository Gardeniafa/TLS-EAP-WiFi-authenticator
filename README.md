TLE EAP Wifi authenticator.  
Used to allow you authentic your devices with 802.1x TLS EAP.  Such as OpenWRT or some enterprise AP/AC.  

How to use?
Clone this repo into your machine, and then use docker build and docker run. In the Dockerfile, does not write port forward config, so you can add it by yourself, or use iptables do this, or you can create macvlan docker-network, and connect this container to it and this is recommended.  
If you dont do any change, the container will auto generante a pair of CA key and CA cert, and use CA key sign server.pem, so do not share your build image to others, this will expose your CA key and server key.  
You can use command sign-client to sign new client cert, finally it will generate <client-name-you-provided>.key/csr/pem/p12 and use CA.key to sign client. So do not share your image, its critical dangerous! Anyone get your image can sign certs for any devices andy any name, your TLS EAP does not secure anymore!  
The .p12 file include CA.pem server.pem and client.pem with client.key, you should install it on your devices, like Windoes/Android/macOS/iOS, the password has auto generate and log on the console, if you have not use -passwd parma to specified it manual.  
Otherwise, some old devices and iOS may not recognize the .p12 file, for this you only need to use -legacy param to use the legacy generte method for compatibility. More about generte client.p12, you can use command `sign-client` without any param to see help.  

Feature:
Support strict CN_name check when use TLE-EAP: the username you have input should strice equas your cert CNname, if not will cause authentication failed.
Compatible with Windows machine based authentication. When install the cert into local machine instead of current user and configure WLAN use Computer based Authentication, When authentication, Windows always add `host/` prefix before cert CN name as the username, and if simply configure username={CN_name} in freeradius, will caused authentication failed. With this feature, it can auto recongize this issue, and not fucked by Microsoft.  
MSchapv2 support, some device, like smart TV or projector, does not support TLS-EAP, you can use username+password authentication, just add username and password into /etc/freeradius/users like the example format.  

Info:
You can revise the Dockerfile does not generate self-sign CA and server cert, just COPY your self designed cert when build. And remember do not share your image to others, it caused significant security issue!  
A scientific trust chain is recommend to build. You can user you self-sign CA and issue a middle CA use to sign clients and buy a domainname, so you can go let's encrypt get free TLS cert, which is trusted by all the devices in the worldwide. Yeah, that means the server cert could be not signed by the client CA, it only used to show the server is trusted or the server could testify that it has the cert for radius.wifi.localnet.example.net, so your devices trust it.  

Todo:
Cert revocation check is not enabled, in other words, when you issued a cert, it will always work before the expire date. So in this background, I will recommend you issue certs shoter and shoter for the temp user and delete your cert before you sales it to used market. If you forget do this, it's only one way to save you security: replace CA and resign your all devices.  
