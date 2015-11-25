#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import re
import urllib
import logging
import bitly_api
import config

logger = logging.getLogger(__name__)


def template(tpl, dictionary=dict()):
    result = tpl
    for item in dictionary.iterkeys():
        result = result.replace(item, dictionary[item])
    return result


def download_url(url, destination_path):
    process = subprocess.Popen(["wget", "-O", destination_path, url], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    return destination_path


def from_text_to_speech(text, audio_path):
    args = ["curl", "http://www.fromtexttospeech.com/",
            "-H", 'Origin: http://www.fromtexttospeech.com',
            "-H", 'Accept-Encoding: gzip, deflate',
            "-H", 'Accept-Language: cs-CZ,cs;q=0.8,en;q=0.6,sk;q=0.4',
            "-H", 'Upgrade-Insecure-Requests: 1',
            "-H",
            'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            "-H", 'Content-Type: application/x-www-form-urlencoded',
            "-H", 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "-H", 'Cache-Control: max-age=0',
            "-H", 'Referer: http://www.fromtexttospeech.com/',
            "-H", 'Connection: keep-alive', "--data",
            "input_text=" + urllib.quote(
                text.encode('utf8')) + "&language=US+English&voice=9&speed=0&action=process_text",
            "--compressed"]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    audio_url = "http://www.fromtexttospeech.com" + re.search("(\/texttospeech_output_files\/\d+\/\d+\.mp3)",
                                                              output).group(0)
    download_url(audio_url, audio_path)


def get_audio_length(audio_path):
    # args = ["ffprobe", "-show_entries", "format=duration", "-i", audio_path]
    args = ["ffprobe", "-show_format", "-i", audio_path]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    return float(re.search("duration=(\d+\.\d+)", output).group(1))


def apply_text(text, fontfile, size=36, color="yellow", movement_x="0", movement_y="0"):
    drawtext = "drawtext=fontfile=" + fontfile + \
               ":text=" + __text_escape(text) + \
               ":fontcolor=" + color + \
               ":fontsize=" + str(size) + \
               ":x=" + str(movement_x) + \
               ":y=" + str(movement_y)
    return drawtext


def __text_escape(text):
    return "'" + text.replace(":", "\\:").replace("'", "'\\\\\\''") + "'"


def run_args(args, cwd=None):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True, cwd=cwd)
    process.communicate()
    result = process.wait()
    if result != 0:
        logger.error("Error while processing command: " + str(args))
    return result


def text_to_file(text, file_path):
    with open(file_path, "w") as text_file:
        text_file.write(text.encode("utf-8"))

def bitly_shorten(url):
    c = bitly_api.Connection(login=config.bitly_login, api_key=config.bitly_api_key)
    return c.shorten(self.get_column("D"))["url"]
