#!/bin/bash
for f in "tocombine"/*.webm
do
if [[ "$f" !=  *"_audio"* ]]; then
filename=$(basename -- "$f")
noext="${filename%%.*}"
audio='tocombine/'"$noext"'_audio.webm'
ffmpeg -i "$f" -i "$audio" -vf yadif -force_key_frames expr:gte\(t\,n_forced/2\) -c:v libx264 -preset ultrafast -crf 18 -bf 2 -c:a aac -q:a 1 -ac 2 -ar 48000 -use_editlist 0 -movflags +faststart "$noext".mp4
wait $!
mv "$noext".mp4 "./streaming"
rm "$f"
rm "$audio"
fi
done
