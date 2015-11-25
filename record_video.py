#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import util
import logging
import time
from youtube import Youtube


class RecordVideo:
    logger = logging.getLogger(__name__)

    def __init__(self, record, cfg):
        self.record = record
        self.config = cfg
        self.video_dir = os.path.join(self.config.video_dir, self.id(), "")
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        self.video_path = os.path.join(self.video_dir, "video.mp4")
        self.audio_dir = os.path.join(self.config.audio_dir, self.id(), "")
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        self.audio_path = os.path.join(self.audio_dir, "audio.mp3")

        self.dictionary = dict()
        index = 0
        for column in record:
            self.dictionary["{{Column" + chr(index + 65) + "}}"] = self.get_column(chr(index + 65))
            index += 1
        if self.config.bitly:
            self.dictionary["{{ColumnD_bitly}}"] = util.bitly_shorten(self.get_column("D"))["url"]
        else:
            self.dictionary["{{ColumnD_bitly}}"] = self.get_column("D")["url"]

    def id(self):
        return self.get_column("B")

    def get_column(self, letter):
        return self.record[ord(letter) - 65]

    def get_images(self):
        self.img_dir = os.path.join(self.config.img_dir, self.get_column("B"))
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
        self.img_paths = []
        index = 0
        for url in self.get_column("I").split(","):
            img_name = url.rsplit('/', 1)[-1]
            # path = os.path.join(self.record_path, str(index).zfill(3) + ".jpg")
            path = os.path.join(self.img_dir, img_name)

            if not self.config.cache_img or not os.path.exists(path):
                util.download_url(url, path)
                time.sleep(1)
            if os.stat(path).st_size > 0:
                self.img_paths.append(path)
            else:
                self.logger.warn("Removed file: " + path + " from url: " + url)
                os.remove(path)
            index += 1

    def create(self):
        self.write_text_files()
        if self.config.cache_video and os.path.exists(self.video_path):
            return

        self.get_images()
        self.fix_images()

        if self.config.use_audio and not os.path.exists(self.audio_path) or not self.config.cache_audio:
            util.from_text_to_speech(self.get_column("J"), self.audio_path)

        if self.config.use_audio:
            audio_length = util.get_audio_length(self.audio_path)
        else:
            audio_length = 45.0

        args3 = ["ffmpeg", "-y", "-t", str(audio_length)]
        index = 0
        # max_ = max(len(self.img_paths), audio_length / 5.0)
        max_ = len(self.img_paths)
        min_ = 0
        for path in self.img_paths:
            if index >= min_ and index < max_:
                args3.extend(["-loop", "1", "-t", "2.5", "-i", path])
            index += 1
        if self.config.use_audio:
            args3.extend(["-i", self.audio_path])

        args3.extend(["-filter_complex"])

        filter = ""
        index = 0
        outputs = ""
        for path in self.img_paths:
            if index >= min_ and index < max_ - 1:
                real_index = index - min_
                i = str(real_index)
                i2 = str(real_index + 1)
                filter += "[" + i2 + ":v][" + i + ":v]blend=all_expr='A*(if(gte(T,0.5),1,T/0.5))+B*(1-(if(gte(T,0.5),1,T/0.5)))'[b" + i2 + "v];\n"
                outputs += "[" + i + ":v][b" + i2 + "v]"
            index += 1

        c = str((real_index + 1) * 2 + 1)
        i = str(real_index + 1)
        filter += outputs + "[" + i + ":" + "v]concat=n=" + c + ":v=1:a=0,format=yuvj422p,"

        text = util.apply_text(self.get_column("A"), self.config.font_file_avenir_black, 36, color="black",
                               movement_x="151",
                               movement_y="51")
        text += "," + util.apply_text(self.get_column("A"), self.config.font_file_avenir_black, 36, color="white",
                                      movement_x="150",
                                      movement_y="50")
        filter += "" + text
        filter += "[v]"

        args3.append(filter)
        args3.extend(["-map", "[v]"])
        if self.config.use_audio:
            args3.extend(["-map", str(max_) + ":0"])
        args3.extend(["-t", str(audio_length), self.video_path])
        if util.run_args(args3) != 0:
            self.logger.warn("Video creation failed!")
            if os.path.exists(self.video_path):
                os.remove(self.video_path)

    def fix_images(self):
        self.logger.debug("Fixing images.")
        util.run_args(
            ["mogrify", "-sampling-factor", "2x2,1x1,1x1", "-resample", "300x300", "-resize", "1024x768!", "*.jpg"],
            cwd=self.img_dir)

    def write_text_files(self):
        title = util.template(self.config.youtube_title, self.dictionary)
        description = util.template(self.config.youtube_description, self.dictionary)
        util.text_to_file(title, os.path.join(self.video_dir, "title.txt"))
        util.text_to_file(description, os.path.join(self.video_dir, "description.txt"))

    def get_csv_row(self):
        row = [
            util.template(self.config.youtube_title, self.dictionary),
            util.template("{{ColumnA}}", self.dictionary),
            util.template(self.config.youtube_description, self.dictionary),
            u"Travel",
            self.video_path
        ]
        row2 = []
        for r in row:
            row2.append(r.replace("\"", "\\\"").replace("\n", " ").replace("\r", " "))
        return row2

    def upload(self):
        self.youtube = Youtube()
        title = util.template(self.config.youtube_title, self.dictionary)
        description = util.template(self.config.youtube_description, self.dictionary)
        category_id = self.config.youtube_category_id
        tags = []
        upload_result = self.youtube.initialize_upload(title, description, self.video_path, category_id, tags)
        self.youtube_videoid = upload_result["id"]

        return upload_result["id"]
