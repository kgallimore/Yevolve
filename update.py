import time
from pytube import YouTube
import sqlite3
import subprocess
import os
import configparser
import requests
from bs4 import BeautifulSoup as bs
import shutil
import json
from urllib import request
import random
import threading
import re

yt = YouTube
audio = video = YouTube.streams
audio_name = video_name = title = ""
api_key = "AIzaSyDXoJOYlFT2zUIwykX-pwd_zbBG4xCujAw"
current_num = 0
stream_process = None
need_dirs = ['streaming', 'conf', 'tocombine']
resolutions = ['1080p', '720p', '480p', '360p', '240p', '144p']
progressive = False
headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
rc = None

def show_progress_bar(chunk, file_handler, bytes_remaining):
    pass
    #print(bytes_remaining)


def download_video(link):
    global audio, video, video_name, audio_name, title, yt, progressive
    while True:
        try:
            while True:
                try:
                    yt = YouTube('https://www.youtube.com/watch?v=' + link)
                except:
                    print("Grabbing Link Error")
                    continue
                break
            yt.register_on_progress_callback(show_progress_bar)
            title = re.sub("[^a-zA-Z]+", "", str(yt.title))
            if len(title) < 3:
                title += 'aaa'
            test_res = yt.streams.filter(file_extension='webm', resolution='1080p').order_by('resolution')
            if test_res:
                while True:
                    try:
                        audio = yt.streams.filter(only_audio=True).order_by('abr')[-1]
                        audio_name = title + '_audio.' + audio.mime_type.split('/')[-1]
                        yt.register_on_complete_callback(download_audio)
                    except Exception as e:
                        print("Grabbing Audio Error")
                        print(e)
                        continue
                    break
            else:
                test_res = yt.streams.filter(progressive=True).order_by('resolution')
                yt.register_on_complete_callback(move_progressive)
            video = test_res[-1]
            video_name = title + '.' + video.mime_type.split('/')[-1]
            video.download(filename=title)
        except Exception as e:
            print("Grabbing Video Error")
            print(e)
            continue
        break


def move_progressive(stream, file_handler):
    print("No Processing Required")
    shutil.move(video_name, 'streaming/' + video_name)


def combine_audio_video(stream, file_handler):
    global rc
    global stream_process
    shutil.move(audio_name, "tocombine/" + audio_name)
    shutil.move(video_name, "tocombine/" + video_name)
    print("Combining")
    rc = subprocess.Popen("./combinewatermark.sh")
    print(rc.communicate())
    print("Done combine")


def download_audio(stream, file_handler):
    global yt
    yt.register_on_complete_callback(combine_audio_video)
    print("Downloading Audio")
    audio.download(filename=title + '_audio')


def get_all_video_in_channel(channel_id):
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


def get_extra_video_info(video_id):
    search_url = "https://www.googleapis.com/youtube/v3/videos?id=" + video_id + "&key=" + api_key + "&part=contentDetails"
    response = request.urlopen(search_url).read()
    data = json.loads(response)
    all_data = data['items']
    content_details = all_data[0]['contentDetails']
    return content_details


def get_video_info(video_id):
    extra = get_extra_video_info(video_id)
    while True:
        content = requests.get('https://www.youtube.com/watch?v=' + video_id)
        soup = bs(content.content, "html.parser")
        dimension = not extra['dimension'] == '2d'
        try:
            result = {'title': soup.find("span", attrs={"class": "watch-title"}).text.strip(),
                      'views': int(soup.find("div", attrs={"class": "watch-view-count"}).text.split(' ')[0].replace(",", "")),
                      'date_published': date_string_to_date(soup.find("strong", attrs={"class": "watch-time-text"}).text),
                      'likes': int(soup.find("button", attrs={"title": "I like this"}).text.replace(",", "")),
                      'dislikes': int(soup.find("button", attrs={"title": "I dislike this"}).text.replace(",", "")),
                      'length': length_string_to_int(extra['duration'][2:]),
                      '3d': dimension}
        except AttributeError:
            continue
        finally:
            break
    return result


def length_string_to_int(length):
    hours = minutes = 0
    if 'M' in length:
        split = length.split('M')
        seconds = split[-1][:-1]
        if "H" in split[0]:
            split = split[0].split("H")
            minutes = split[-1]
            hours = split[0]
        else:
            minutes = split[0]
    else:
        seconds = length[:-1]
    return 3600 * int(hours) + 60 * int(minutes) + int(seconds)


def date_string_to_date(date):
    split = date.split(' ')
    month_abbr = split[-3].lower()
    day = split[-2].replace(',', '')
    year = split[-1]
    month = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }[month_abbr]
    return f"{year}/{month}/{day}"


def insert_video_database(channel_id):
    with create_conn('conf/conf.db') as conn:
        videos = get_all_video_in_channel(channel_id)
        c = conn.cursor()
        print("Adding " + str(len(videos)) + " videos to database")
        for vid in videos:
            sql = "SELECT * FROM videos WHERE video_id = ?"
            c.execute(sql, (vid,))
            if c.fetchone() is None:
                data = get_video_info(vid)
                sql = "INSERT INTO videos (video_id, video_length, title, threeD, views, date_published, likes, dislikes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                c.execute(sql, (vid, int(data['length']), data['title'], bool(data['3d']), int(data['views']), data['date_published'], int(data['likes']), int(data['dislikes']),))
                conn.commit()


def create_conn(db):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db)
    except Exception as e:
        exit(e)
    finally:
        return conn


def setup_database():
    sql_commands = [
        'CREATE TABLE settings (channel_id STRING PRIMARY KEY UNIQUE NOT NULL, current_num INTEGER DEFAULT (0))',
        'CREATE TABLE videos (video_id STRING PRIMARY KEY NOT NULL UNIQUE, played_at DATETIME DEFAULT (0), num_plays INTEGER DEFAULT (0), video_length INTEGER NOT NULL, title STRING NOT NULL, threeD BOOLEAN DEFAULT (FALSE) NOT NULL, views INTEGER NOT NULL, date_published DATE NOT NULL, likes INTEGER NOT NULL, dislikes INTEGER NOT NULL)']

    with create_conn('conf/conf.db') as conn:
        c = conn.cursor()
        for command in sql_commands:
            c.execute(command)
        conn.commit()


def get_config():
    for directory in need_dirs:
        if not os.path.isdir(directory):
            os.mkdir(directory)
    config = configparser.ConfigParser()
    if not os.path.isfile('conf/conf.db'):
        f = open('conf/conf.db', "w")
        f.close()
        setup_database()
    if not os.path.isfile('conf/conf.ini'):
        config.add_section('Channel Data')
        channel_id = input('Channel ID:')
        config['Channel Data']['channel_id'] = channel_id
        with open('conf/conf.ini', 'w') as conf_file:
            config.write(conf_file)
        return channel_id
    config.read('conf/conf.ini')
    return config['Channel Data']['channel_id']


def setup_channel(channel_id):
    insert_video_database(channel_id)


def select_video(max_length):
    with create_conn('conf/conf.db') as conn:
        c = conn.cursor()
        sql = 'SELECT video_id, num_plays FROM videos WHERE threeD = FALSE AND video_length < ? ORDER BY num_plays ASC, played_at ASC'
        c.execute(sql, (max_length,))
        result = c.fetchall()
        max_rand = min(3, len(result)-1)
        chosen = result[random.randint(0,max_rand)]
        if result:
            return chosen[0]
        else:
            return False


def main(max_length):
    global stream_process
    num_files = len(os.listdir('streaming'))
    if stream_process is None and num_files > 0:
        stream_process = subprocess.Popen('./stream.sh')
    if num_files < 3:
        rand_vid = select_video(max_length)
        if rand_vid is not False:
            download_video(rand_vid)


if __name__ == '__main__':
    try:
        while True:
            time.sleep(1)
            main(300)
    except KeyboardInterrupt:
        if stream_process is not None:
            stream_process.kill()
        if stream_process is not None:
            rc.kill()


