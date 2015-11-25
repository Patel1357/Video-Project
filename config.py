#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

__assets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "")
__font_dir = os.path.join(__assets_dir, "font", "")

video_dir = os.path.join(__assets_dir, "video", "")
img_dir = os.path.join(__assets_dir, "img", "")
audio_dir = os.path.join(__assets_dir, "audio", "")

tmp_dir = os.path.join(__assets_dir, "tmp", "")

data_path = os.path.join(__assets_dir, "data2.csv")

height = 768
width = 1024
size = str(width) + "x" + str(height)
scale = str(width) + ":" + str(height)

font_file_avenir_black = os.path.join(__font_dir, "Avenir-Black.ttf")

youtube_title = "{{ColumnA}} - {{ColumnF}}, {{ColumnG}}"
youtube_description = u"""Book here: {{ColumnD_bitly}}

Address: {{ColumnE}}, {{ColumnF}}, {{ColumnG}} {{ColumnH}}

{{ColumnJ}}"""
#if bitly is configured, you can use ColumnD_bitly
cache_audio = True
cache_video = True
cache_img = True
upload = False
use_audio = True

append_csv = True

output_csv_path = os.path.join(__assets_dir, "output.csv")

# travel and events
youtube_category_id = 19

bitly = True
bitly_api_key = "R_66e31e1a11ea41189a69e07d04ef46df"
bitly_login = "karelhovorka"

