#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class Youtube:
    def __init__(self, secrets_file="client_secrets.json"):
        self.service = None
        httplib2.RETRIES = 1
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                                     httplib.IncompleteRead, httplib.ImproperConnectionState,
                                     httplib.CannotSendRequest, httplib.CannotSendHeader,
                                     httplib.ResponseNotReady, httplib.BadStatusLine)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        self.CLIENT_SECRETS_FILE = secrets_file
        self.scope = "https://www.googleapis.com/auth/youtube"
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"

        self.MISSING_CLIENT_SECRETS_MESSAGE = """
        WARNING: Please configure OAuth 2.0

        To make this sample run you will need to populate the client_secrets.json file
        found at:

           %s

        with information from the Developers Console
        https://console.developers.google.com/

        For more information about the client_secrets.json file format, please visit:
        https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           self.CLIENT_SECRETS_FILE))

        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

        self.__get_authenticated_service(argparser.parse_args([], None))

    def __get_authenticated_service(self, args):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
                                       scope=self.scope,
                                       message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)
        self.service = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                             http=credentials.authorize(httplib2.Http()))
        return self.service

    def initialize_upload(self, title, description, video_path, category_id, tags=[]):

        body = dict(
            snippet=dict(
                title=title,
                description=description,
                tags=tags,
                categoryId=category_id
            ),
            status=dict(
                privacyStatus="public"
            )
        )
        insert_request = self.service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )

        return self.__resumable_upload(insert_request)

    def __resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print "Uploading file..."
                status, response = insert_request.next_chunk()
                if 'id' in response:
                    print "Video id '%s' was successfully uploaded." % response['id']
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
            except HttpError, e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS, e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print error
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print "Sleeping %f seconds and then retrying..." % sleep_seconds
                time.sleep(sleep_seconds)
        return response

    def set_thumbnail(self, video_id, thumbnail_path):
        set_result = self.service.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_path
        ).execute()
        return set_result

    def update_video(self, video_id, title=None, description=None, tags=None, category_id=None):
        snippet_ = dict()
        if title is not None:
            snippet_["title"] = title
        if description is not None:
            snippet_["description"] = description
        if tags is not None:
            snippet_["tags"] = tags
        if category_id is not None:
            snippet_["categoryId"] = category_id

        videos_update_response = self.service.videos().update(
            part='snippet',
            body=dict(
                snippet=snippet_,
                id=video_id
            )).execute()
        return videos_update_response

    def list_video_by_id(self, video_id):
        videos_list_response = self.service.videos().update(
            part='snippet',
            body=dict(
                id=video_id
            )).execute()
        return videos_list_response

    def create_playlist(self, title, description, privacy_status="public"):
        playlists_insert_response = self.service.playlists().insert(
            part="snippet,status",
            body=dict(
                snippet=dict(
                    title=title,
                    description=description
                ),
                status=dict(
                    privacyStatus=privacy_status
                )
            )
        ).execute()
        return playlists_insert_response

    def update_playlist(self, playlist_id, title_, description=None, privacy_status="public"):
        body_ = dict(
                id=playlist_id,
                snippet=dict(
                    title=title_
                ),
                status=dict(
                    privacyStatus=privacy_status
                ))
        if description is not None:
            body_["snippet"]["description"] = description
        playlists_update_response = self.service.playlists().update(
            part="snippet,status",
            body=body_
        ).execute()
        return playlists_update_response

    def list_playlist(self, playlist_ids, max_results=50):
        playlists_list_response = self.service.playlists().list(
            part="snippet,status",
            id=",".join(playlist_ids),
            maxResults=max_results
        ).execute()
        return playlists_list_response

    def delete_playlist(self, playlist_id):
        playlist_delete_response = self.service.playlists().delete(
            id=playlist_id
        ).execute()
        return playlist_delete_response

    def add_video_to_playlist(self, playlist_id, video_id):
        playlistitems_insert_response = self.service.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                    # 'position': 0
                }
            }
        ).execute()
        return playlistitems_insert_response

    def list_playlistitems_all(self, playlist_id):
        playlistitems_list_response = self.service.playlistItems().list(
            playlistId=playlist_id,
            part="snippet",
            maxResults=50
        ).execute()
        last_result = playlistitems_list_response
        while "nextPageToken" in last_result:
            new_result = self.list_playlistitems(playlist_id, 50, last_result["nextPageToken"])
            playlistitems_list_response["items"].extend(new_result["items"])
            last_result = new_result

        return playlistitems_list_response


    def list_playlistitems(self, playlist_id, max_results=50, page_token=None):
        playlistitems_list_response = self.service.playlistItems().list(
            playlistId=playlist_id,
            part="snippet",
            maxResults=max_results,
            pageToken=page_token
        ).execute()
        return playlistitems_list_response

    def update_playlistitem(self, playlist_id, playlistitems_id, video_id, position):
        playlistitems_update_response = self.service.playlistItems().update(
            part="snippet, status",
            body={
                'id': playlistitems_id,
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    },
                    'position': position
                }
            }
        ).execute()
        return playlistitems_update_response

    def delete_playlistitem(self, playlistitems_id):
        playlistitems_delete_response = self.service.playlistItems().delete(
            id=playlistitems_id
        ).execute()
        return playlistitems_delete_response
