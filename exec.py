#!/usr/bin/python
# -*- coding: utf-8 -*-

import config as config
import logging, sys
from record_video import RecordVideo
from unicode_csv_reader import UnicodeCsvReader

logger = logging.getLogger(__name__)

with open(config.data_path, 'r') as csv_file:
    reader = UnicodeCsvReader(csv_file)

    index = 0
    for row in reader:
        recordVideo = RecordVideo(row, config)
        logger.info("Starting with video id: " + str(recordVideo.id()))
        recordVideo.create()
        recordVideo.write_text_files()
        if config.upload:
            logger.debug("Starting with upload: " + str(recordVideo.id()))
            youtube_id = recordVideo.upload()
        if config.append_csv:
            with open(config.output_csv_path, "a") as output_file:
                line = "\"" + "\",\"".join(recordVideo.get_csv_row()) + "\""
                output_file.write(line.encode("utf-8") + "\n")
