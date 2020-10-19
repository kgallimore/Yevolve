#!/bin/bash
for f in "tocombine"/*.webm
do
if [[ "$f" !=  *"_audio"* ]]; then
filename=$(basename -- "$f")
noext="${filename%%.*}"
audio='tocombine/'"$noext"'_audio.webm'
ffmpeg -i "$f" -i "$audio" -vf yadif -vf drawtext="fontfile=TitilliumWeb-Black.ttf: text='Yevolve': fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5: boxborderw=5: x=(w-text_w)\/2: y=0" -force_key_frames expr:gte\(t\,n_forced/2\) -c:v libx264 -preset ultrafast -crf 28 -bf 2 -c:a aac -q:a 1 -ac 2 -ar 48000 -use_editlist 0 "$noext".mp4
wait $!
mv "$noext".mp4 "./streaming"
rm "$f"
rm "$audio"
fi
done

