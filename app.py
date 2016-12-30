# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
import requests
import os
from argparse import ArgumentParser

import msocr
import image_management
import db_access

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)

from linebot.http_client import (
        HttpClient, RequestsHttpClient,RequestsHttpResponse
)

from MyRequestsHttpClient import MyRequestsHttpClient

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = "e37fb3dbdef6a04f07cded58e3333f38"
channel_access_token = "IlQKA+p8nuk2tQWFI2rAUmIT/6Eewpse8o3wtSY3g0vqmO9XiygI+UlnsxvpwDqQL1DpmHQ3mS0YvIOmSQkeqohdLzs1JYGiwERQ9hi/k9NP0wQJvSlpJ1o8NqbXyXudoHodBOFCvlWR/jNnIhnYXgdB04t89/1O/w1cDnyilFU="

line_bot_api = LineBotApi(channel_access_token, http_client=MyRequestsHttpClient)
parser = WebhookParser(channel_secret)

@app.route("/")
def main():
    return 'hello daniel'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #print "Request body: " + body

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            processTextMessage(event)
        elif isinstance(event.message, ImageMessage):
            processImageMessage(event)

    return 'OK'

def processTextMessage(event):
    userId = event.source.sender_id
    profile = line_bot_api.get_profile(userId)

    results = db_access.findImageWithCaption(userId, res) 
    if results:
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(results[0]['url']))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="@" + profile.display_name + ": " + event.message.text))

        #line_bot_api.push_message( userId, TextSendMessage(text='push yo, ' + profile.display_name))

def processImageMessage(event):
    userId = event.source.sender_id

    # get binary
    message_content = line_bot_api.get_message_content(event.message.id)
    image_binary = message_content.content

    # get ocr text
    res = msocr.ocr_with_content(image_binary)

    # save image to cloudinary
    fp = open("tmp_img", "wb")
    fp.write(image_binary)
    fp.close()
    url, imageId = image_management.upload(userId, "tmp_img")

    # save image to db
    db_access.addImage(userId, imageId, url, res) 

    # send ocr text message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=res)
    )

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=80, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
