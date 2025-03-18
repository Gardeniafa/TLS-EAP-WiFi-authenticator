TLS EAP Wifi authenticator.  
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

** ZH_CN version **   
translated by doubao.com  
### TLS EAP Wi-Fi 认证器

哇哦！这是一个超厉害的 TLS EAP Wi-Fi 认证器哟😎！它能让你用 802.1x TLS EAP 方式给设备认证呢，像 OpenWRT 或者一些企业级的 AP/AC 都能用得上哒😜。

#### 怎么使用呀🧐
首先呢，你要把这个仓库克隆到你的机器上哟，就像这样：
```bash
git clone <项目仓库地址>
```
然后就可以用 Docker 来构建和运行容器啦😏。不过呢，Dockerfile 里可没写端口转发的配置哦，你可以自己加进去，或者用 `iptables` 来搞定，又或者创建一个 `macvlan` Docker 网络，把容器连上去，这个方法我超推荐哒😘。

要是你啥都不改，容器就会自动生成一对 CA 密钥和 CA 证书，还会用 CA 密钥去签署 `server.pem` 呢。但是哦，可千万别把你构建好的镜像分享给别人呀，不然你的 CA 密钥和服务器密钥就会暴露出去哒，那就像把城堡的钥匙随便给别人一样危险😱！

你可以用 `sign-client` 命令来签署新的客户端证书哟，最后会生成 `<你提供的客户端名称>.key`、`.csr`、`.pem` 和 `.p12` 文件，还会用 CA.key 来签署客户端呢。所以呀，一定一定不要分享你的镜像哦，这超级危险哒😈！要是别人拿到你的镜像，就能给任何设备和任何名称签署证书，那你的 TLS EAP 就一点都不安全啦🥹！

`.p12` 文件里包含了 `CA.pem`、`server.pem` 和 `client.pem` 以及客户端密钥哟，你要把它安装到你的设备上，像 Windows、Android、macOS 或者 iOS 设备都可以哒😎。如果没有用 `-passwd` 参数手动指定密码，密码会自动生成，还会在控制台显示出来哒😜。

不过呢，有些老设备还有 iOS 设备可能识别不了 `.p12` 文件哦，这时候你只要用 `-legacy` 参数，用旧的生成方法就能解决兼容性问题啦😏。要是你想了解更多生成客户端 `.p12` 文件的方法，就用 `sign-client` 命令，啥参数都不加，就能看到帮助信息啦🤓。

#### 特色功能😎
- **严格的 CN 名称检查**：在使用 TLE - EAP 时，它支持严格的 CN 名称检查哟😏。就是说你输入的用户名得和证书的 CN 名称完全一样，不然认证就会失败哒😜。
- **和 Windows 机器认证兼容**：它和基于 Windows 机器的认证超兼容哒😘。当你把证书安装到本地机器而不是当前用户，并且配置 WLAN 使用基于计算机的认证时，Windows 认证的时候总会在证书 CN 名称前面加上 `host/` 前缀作为用户名。要是在 FreeRADIUS 里简单地把用户名配置成 `{CN_name}`，认证就会失败哒😫。但是有了这个功能，它就能自动识别这个问题，才不会被微软搞得晕头转向呢😎！
- **支持 MSchapv2**：有些设备，像智能电视或者投影仪，可能不支持 TLS - EAP，没关系哒😜！你可以用用户名 + 密码的认证方式，只要把用户名和密码按照示例格式添加到 `/etc/freeradius/users` 文件里就行啦😏。

#### 小提示😉
你可以修改 Dockerfile，让它在构建的时候不生成自签名的 CA 和服务器证书，而是在构建的时候复制你自己设计的证书哟😎。但是别忘了，可千万别把你的镜像分享给别人，这会造成很严重的安全问题哒😱！

我还建议你构建一个科学的信任链哟😏。你可以用自己签名的 CA 签发一个中间 CA 来签署客户端，再买个域名，然后去 Let's Encrypt 获取免费的 TLS 证书，这个证书可是全世界的设备都信任的呢😎！这就意味着服务器证书可以不用客户端 CA 来签署，它只是用来证明服务器是可信的，或者证明服务器有 `radius.wifi.localnet.example.net` 的证书，这样你的设备就会信任它啦😘。

#### 待办事项😜
目前还没有启用证书撤销检查哦，也就是说，你签发的证书在有效期内会一直有效哒😏。所以呢，我建议你给临时用户签发有效期越来越短的证书，在把设备卖给二手市场之前删掉证书哟😉。要是你忘了这么做，想要保证安全就只有一个办法啦，就是更换 CA，然后重新给所有设备签署证书😱！

好啦，就这么多啦，快去试试这个超棒的认证器吧😘！ 
