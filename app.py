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
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    PostbackEvent, MessageEvent,
    TextMessage, ImageMessage,
    TextSendMessage, ImageSendMessage, TemplateSendMessage,
    ConfirmTemplate,
    PostbackTemplateAction, MessageTemplateAction,
    SourceUser
)

from linebot.http_client import (
        HttpClient, RequestsHttpClient, RequestsHttpResponse
)
from linebot.exceptions import (LineBotApiError)

from MyRequestsHttpClient import MyRequestsHttpClient

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = "e37fb3dbdef6a04f07cded58e3333f38"
channel_access_token = "IlQKA+p8nuk2tQWFI2rAUmIT/6Eewpse8o3wtSY3g0vqmO9XiygI+UlnsxvpwDqQL1DpmHQ3mS0YvIOmSQkeqohdLzs1JYGiwERQ9hi/k9NP0wQJvSlpJ1o8NqbXyXudoHodBOFCvlWR/jNnIhnYXgdB04t89/1O/w1cDnyilFU="

line_bot_api = LineBotApi(channel_access_token, http_client=MyRequestsHttpClient)
handler = WebhookHandler(channel_secret)

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
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    userId = event.source.sender_id
    text = event.message.text

    results = db_access.findImageWithCaption(userId, text).limit(5)
    if results and results.count() > 0:
        images = []
        for r in results:
            original_url = r['url']
            #print original_url
            preview_url = image_management.getPreviewImage(r['imageId'])
            #print preview_url
            image = ImageSendMessage(original_content_url=original_url , preview_image_url=preview_url)
            images.append(image)
        try:
            line_bot_api.reply_message( event.reply_token,images)

        except LineBotApiError as e:
            print(e.status_code)
            print(e.error.message)
    else:
        prefix = ""
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(userId)
            prefix = "@" + profile.display_name + ": "
        else:
            return

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=prefix + text))

        #line_bot_api.push_message( userId, TextSendMessage(text='push yo, ' + profile.display_name))

@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    userId = event.source.sender_id

    # get binary
    message_content = line_bot_api.get_message_content(event.message.id)
    image_binary = message_content.content

    # get ocr text
    res = msocr.ocr_with_content(image_binary)

    if not res or res == "":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="can't find words"))
        return

    # show confirm message
    confirm_template = ConfirmTemplate(text='辨識結果：' + res, actions=[
        PostbackTemplateAction(label='Save',
                               data='saveImage@#' + event.message.id + '@#' + userId + '@#' + res),
        MessageTemplateAction(label='No', text='Discard image.'),
    ])

    template_message = TemplateSendMessage(
        alt_text='Save image is not supported', template=confirm_template)
    line_bot_api.reply_message(event.reply_token, template_message)

@handler.add(PostbackEvent)
def handle_postback(event):
    #print event.postback.data
    userId = event.source.sender_id
    # 0:action, 1: messageId, 2: userId, 3: caption
    info = event.postback.data.split("@#")

    # check if userId is the same
    if userId != info[2]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='The image is not uploaded by you.'))
        return

    if info[0] == "saveImage":
        if saveImage(info[1], info[2], info[3]) == "savedBefore":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Saved before.'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Image is saved.'))

def saveImage(messageId, userId, caption):
    # check if image is already saved, if so, return saved
    print "messageId",messageId
    if db_access.findImageWithMessageId(messageId).count() > 0:
        return "savedBefore"
    print "findImageWithMessageId:",db_access.findImageWithMessageId(messageId).count()

    message_content = line_bot_api.get_message_content(messageId)
    image_binary = message_content.content

    # save image to cloudinary
    fp = open("tmp_img", "wb")
    fp.write(image_binary)
    fp.close()
    url, imageId = image_management.upload(userId, "tmp_img")

    # save image to db
    db_access.addImage(userId, imageId, url, caption)

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=80, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
