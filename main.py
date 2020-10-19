from pytube import YouTube
import json
from urllib import request
import ffmpeg
import pylivestream
import sys
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess
import os
import pyfakewebcam

yt = YouTube
audio = video = YouTube.streams
audio_name = video_name = title = None
api_key = "AIzaSyDXoJOYlFT2zUIwykX-pwd_zbBG4xCujAw"
R = Path(__file__).resolve().parent
sites = ['youtube',]
VIDFN = R / 'finished_video.mp4'
LOGO = R.parent / 'doc' / 'logo.png'
TIMEOUT = 30


def test_props(periscope_kbps):
    S = pls.FileIn(inifn=None, websites=sites, infn=VIDFN, key='abc')
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps == approx(24.)

        if s == 'periscope':
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


def test_audio(periscope_kbps):
    flist = list(R.glob('*.ogg'))

    S = pls.FileIn(inifn=None, websites=sites, infn=flist[0], key='abc')
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps is None


def show_progress_bar(chunk, file_handler, bytes_remaining):
    print(bytes_remaining)


def download_video(link):
    global audio, video, video_name, audio_name, title, yt
    yt = YouTube(link)
    title = str(yt.title).replace(" ", "")
    video = yt.streams.order_by('resolution')[-1]
    audio = yt.streams.filter(only_audio=True).order_by('abr')[-1]
    video_name = title + '_video.' + video.mime_type.split('/')[-1]
    audio_name = title + '_audio.' + audio.mime_type.split('/')[-1]
    yt.register_on_progress_callback(show_progress_bar)
    yt.register_on_complete_callback(download_audio)
    video.download(filename=title + '_video')


def combine_audio_video(stream, file_handler):
    print(video_name)
    print(audio_name)
    video_in = ffmpeg.input(video_name).video
    audio_in = ffmpeg.input(audio_name).audio
    ffmpeg.concat(video_in, audio_in, v=1, a=1).output('finished_video.mp4').run_async()


def download_audio(stream, file_handler):
    global yt
    yt.register_on_complete_callback(combine_audio_video)
    audio.download(filename=title + '_audio')


def get_all_video_in_channel(channel_id):

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key,
                                                                                                        channel_id)

    video_links = []
    url = first_url
    while True:
        inp = request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links


def get_video_length(video_id):
    search_url = "https://www.googleapis.com/youtube/v3/videos?id=" + video_id + "&key=" + api_key + "&part=contentDetails"
    response = request.urlopen(search_url).read()
    data = json.loads(response)
    all_data = data['items']
    content_details = all_data[0]['contentDetails']
    return content_details['duration'][2:]


def live_stream():
    stream = pylivestream.Livestream(inifn=Path(os.getcwd()), site='youtube')
    stream2 = pylivestream.FileIn(Path(os.getcwd()), websites='youtube')
    stream.filein()
    stream.key = 'tusm-dmxq-zp33-2mt2'
    stream.startlive()



print()
"""for video in get_all_video_in_channel("UCCoLOMOARSd4XRT358Le-LA"):
    print(get_video_length(video))
"""


def test_simple():
    """stream to localhost
    """
    S = pls.FileIn(inifn=None, websites='youtube',
                   infn=R / 'finished_video.mp4',
                   yes=True, timeout=99999, key='vr6t-wcyh-7g7w-p3q7-fpr4')

    S.golive()


def test_script():
    subprocess.check_call([sys.executable, 'Glob.py',
                           str(VIDFN),
                           'localhost',
                           '--yes', '--timeout', '5'],
                          timeout=TIMEOUT, cwd=R.parent)


if __name__ == '__main__':
    test_simple()