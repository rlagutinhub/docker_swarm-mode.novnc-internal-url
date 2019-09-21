# noVNC Display Container + Docker services internal url
```
```
This image is intended to be used for displaying x11 applications from container in a browser.
>	* Base image oraclelinux:7-slim

FYI https://github.com/rlagutinhub/docker.novnc

***

## Image Contents

* [xvfb](http://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml) - x11 in a virtual framebuffer
* [x11vnc](http://www.karlrunge.com/x11vnc/) - a VNC server that scrapes the above X11 server
* [noVNC](https://kanaka.github.io/noVNC/) - a HTML5 canvas vnc viewer
* [fluxbox](http://www.fluxbox.org/) - a small window manager
* [conky](https://github.com/brndnmtthws/conky) - light-weight system monitor for X
* [xterm](http://invisible-island.net/xterm/) - to demo that it works
* [firefox](https://www.mozilla.org) - web browser developed by the Mozilla Foundation
* [supervisord](http://supervisord.org) - to keep it all running

Build image:
`docker build -f Dockerfile -t docker_swarm-mode.novnc-internal-url .`

## Usage

### Variables

You can specify the following variables:
* `DISPLAY_WIDTH=<width>` (1024)
* `DISPLAY_HEIGHT=<height>` (768)
* `VNC_PASS=<password>` (passw0rd)

### Properties
```vim docker-services.internal-url.json```
* `srv_name` - need to specify service name
* `proto` - need to specify http or https protocol
* `port` - need to specify used tcp port (for example 8080)
* `url_appned` - appned url (for example /console)
```console
[
    {"srv_name": "hello1", "proto": "http", "port": "8000", "url_append": "/"},
    {"srv_name": "hello2", "proto": "http", "port": "8000", "url_append": "/"},
    {"srv_name": "hello3", "proto": "https", "port": "8000", "url_append": "/"}
]
```

### Swarm Mode
Run with custom settings:
`docker stack deploy --compose-file docker-compose.yml vnc`
```console
version: '3.7'
services:
  app:
    image: rlagutinhub/docker_swarm-mode.novnc-internal-url:latest
    networks:
      - proxy
    environment:
      - "DISPLAY_WIDTH=1920"
      - "DISPLAY_HEIGHT=899"
      - "VNC_PASS=123456"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    configs:
      - source: vnc_docker-services.internal-url.json.2019-09-21
        target: /app/docker-services.internal-url.json
    shm_size: 256mb
    stop_grace_period: 1m
    deploy:
      # mode: global
      replicas: 1
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 10s
        max_attempts: 3
        window: 120s
      labels:
        # https://docs.traefik.io/configuration/backends/docker/#on-containers
        - "traefik.enable=true"
        - "traefik.port=6080"
        # - "traefik.weight=10"
        - "traefik.frontend.rule=Host:vnc.docker.example.com,vnc.docker.test.example.com"
        # - "traefik.frontend.rule=Host:vnc.docker.example.com,vnc.docker.test.example.com;PathPrefixStrip:/app"
        - "traefik.frontend.entryPoints=http"
        # - "traefik.frontend.entryPoints=http,https"
        # - "traefik.frontend.headers.SSLRedirect=true"
        # - "traefik.frontend.auth.basic.users=root:$$apr1$$mLRjS/wr$$QqrALWNDgW9alDmnb9DeK1"
        # - "traefik.backend.loadbalancer.stickiness=true"
        - "traefik.backend.loadbalancer.method=wrr"
      placement:
        constraints:
          - node.role == manager
          # - node.role == worker
          # - node.labels.novnc == true
networks:
  proxy:
    external: true
# volumes:
  # logs:
    # external: true
configs:
  vnc_docker-services.internal-url.json.2019-09-21:
    external: true
```

![alt text](https://raw.githubusercontent.com/rlagutinhub/docker.novnc-internal-url/master/screen1.png)

### Result
Open a browser and see the `xterm` and `firefox` demo at `http://<server>`

![alt text](https://raw.githubusercontent.com/rlagutinhub/docker.novnc-internal-url/master/screen2.png)

## On DockerHub / GitHub
___
* DockerHub [rlagutinhub/docker_swarm-mode.novnc-internal-url](https://hub.docker.com/r/rlagutinhub/docker_swarm-mode.novnc-internal-url)
* GitHub [rlagutinhub/docker_swarm-mode.novnc-internal-url](https://github.com/rlagutinhub/docker_swarm-mode.novnc-internal-url)
