#!/usr/bin/python
# -*- coding: utf-8 -*-


import config
from record_video import RecordVideo
from util import UnicodeReader

with open(config.data_path, 'r') as csv_file:
    reader = UnicodeReader(csv_file)

    description_characters = 0
    min_description_characters = 9999
    max_description_characters = 0
    records = 0
    images = 0
    min_images = 9999
    max_images = 0
    record = reader.next()
    while record is not None:
        recordVideo = RecordVideo(record, config)
        description_characters += len(recordVideo.get_column("J"))
        i = len(recordVideo.get_column("I").split(","))
        images += i
        if i < min_images:
            min_images = i
        if i > max_images:
            max_images = i
        records += 1
        try:
            record = reader.next()
        except:
            StopIteration
            record = None

    print "Records: " + str(records)
    print "Description characters per record: " + str(description_characters / records)
    print "Images per record: " + str(images / records) + "(" + str(min_images) + " - " + str(max_images) + ")"
    print "Estimated characters: " + str(description_characters / records * 40000)
