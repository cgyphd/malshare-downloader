# malshare_downloader

This project downloads malwares from malshare.com with using malshare api since 2013.04.06. The project has a proxy which is from https://blog.jessfraz.com/post/tor-socks-proxy-and-privoxy-containers/.   

# Getting Started

Docker containers work in background in the project. If users want to use proxy, they should install docker.

# Installing 

```
pip install -r requirements.txt
```
# Usage

Add your api key(s) in the config.cfg.
```
config.cfg
            lastupdated:2013-04-06
            keys:API_KEY1:API_KEY2
```
```
python malshare.py
```

# License

This project is licensed under the MIT License - see the LICENSE.md file for details
