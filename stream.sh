#!/bin/bash
RTMP_URL="rtmp://a.rtmp.youtube.com/live2"
STREAM_KEY="7szj-bmmx-w134-r92g-cs3h"
OUTPUT=$RTMP_URL/$STREAM_KEY
FILES=streaming
DIR='streaming/'
while true
do
	for f in $FILES/*.mp4
	do
	test -f "$f" || continue
	ffmpeg -re -i "$f" -vcodec copy -c:a copy -map 0 -f flv $OUTPUT -nostdin
	wait $!
	rm $f
	done
done
