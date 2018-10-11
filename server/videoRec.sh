#!/bin/bash

recording_time=$(($1 * 1000))
num_vid=$2

i=0
while [ $i -lt $num_vid ]; do
	raspivid -n -o vid_scp.h264 -t $recording_time -co 30 -br 60 -ISO 700 -md 0 -ex "backlight" -mm "backlit"
	vid="vid_"`date +"%d%m%y-%H%M%S"`.h264
	sshpass -p "nebbia" scp vid_scp.h264 nebbia@10.64.22.197:/data/piVid/280618/$vid
	rm vid_scp.h264
	i=$(($i + 1))
done
