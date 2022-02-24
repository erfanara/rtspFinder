Restream the rtsp

# Restream the rtsp

## Table of contents
* [Method_1](#Method_1)
	* [Requirements](#Requirements)
	* [Description](#Description)
		* [launch-a-RTSP-server](#launch-a-RTSP-server)
			* [Configuration](#Configuration)
		* [Restream](#Restream)
* [Method_2](#Method_2)
	* [limits](#limits)
* [Method_3](#Method_3)
	* [limits](#limits)

## Method_1
### Requirements
1. restreamer using ffmpeg in the local network of dvr/nvr/cameras
2. rtsp server with public ip in internet

### Description
First we need a accessable rtsp server in the internet.

rtsp servers have publish user and read user:
- publish user is able to send data to the rtsp server.
- read user is able to receive data from rtsp server.

#### launch-a-RTSP-server
we can use https://github.com/aler9/rtsp-simple-server to run a rtsp server using docker.
`docker run --rm -it --network=host aler9/rtsp-simple-server` 

you can use `-d` instead of `-it` if you want to run the container in the background instead of interactive mode.

##### Configuration
All the configuration parameters are listed and commented in the [configuration file](https://github.com/aler9/rtsp-simple-server/blob/main/rtsp-simple-server.yml).

Please take a look at [Configuration methods](https://github.com/aler9/rtsp-simple-server/blob/main/README.md#configuration). I used the first way to config the server.

you should change these in the `rtsp-simple-server.yml`:
- publishUser, publishPass (take a look at this [section](https://github.com/aler9/rtsp-simple-server/blob/main/README.md#authentication))
- readUser, readPass
- disable unnecessary ports like rtmp and hls

So one can run the server like this: 
     ```
     docker run --rm -d --network=host -v $PWD/rtsp-simple-server.yml:/rtsp-simple-server.yml aler9/rtsp-simple-server
     ```

this will use `rtsp-simple-server.yml` in the directory you are in.


#### Restream 
after launching the rtsp server. you can restream your desired stream to the rtsp server.
`ffmpeg -re -i "<INPUT_STREAM>" -c copy -f rtsp "rtsp://<publishUser>:<publishPass>@localhost:8554/mystream123"`

- `-re` : Read input at native frame rate. It is useful for real-time output.
- `-i "<INPUT_STREAM>"` : put your desired input stream here, for example: *"rtsp://admin:123456@192.168.1.2:554/cam1"*
- `-c copy` : just copy the input stream and do not change the codec
- `-f rtsp "rtsp://<publishUser>:<publishPass>@localhost:8554/mystream123"` :  this rtsp url should point to publish url of your rtsp server. you can also change `mystream123` if you want.

## Method_2 (no need to public server) :
In this method we assume that we don't have any server. also in this method we use instruction from method_1.
but we use p2p VPNs like tailscale to atone the lack of public server and to bypass limitation of NATs.
1. you should just install the tailscale on the computer outside of your local network and the computer inside the local network where you have access to your cameras. and then you should connect both computers to one tailscale account.
2. Now you can run rtsp server on the local computer(read Method_1), and then you can connect to that rtsp server from outside computer.
### limits
-  their can be bandwitch limits if number of clients increase
-  p2p VPNs are sometimes unstable

## Method_3 (port forwarding or dmz):
In this method we should change the NAT (your router) settings. so you should access to the your NAT settings.
### limits
- you should access to the your NAT settings
- their can be bandwitch limits if number of clients increase
- this method depends on isp
