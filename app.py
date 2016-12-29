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

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.http_client import (
        HttpClient, RequestsHttpClient,RequestsHttpResponse
)

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

english_bot = ChatBot("English Bot")
english_bot.set_trainer(ChatterBotCorpusTrainer)
english_bot.train("chatterbot.corpus.english.conversations")

app = Flask(__name__)

proxies = {
        "http": os.environ['QUOTAGUARDSTATIC_URL'],
        "https": os.environ['QUOTAGUARDSTATIC_URL']
        }

class MyRequestsHttpClient(RequestsHttpClient):
    def __init__(self, timeout=HttpClient.DEFAULT_TIMEOUT):
        super(RequestsHttpClient, self).__init__(timeout)

    def get(self, url, headers=None, params=None, stream=False, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = requests.get(
            url, headers=headers, params=params, stream=stream, timeout=timeout, proxies = proxies
        )

        return RequestsHttpResponse(response)

    def post(self, url, headers=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = requests.post(
            url, headers=headers, data=data, timeout=timeout, proxies = proxies
        )

        return RequestsHttpResponse(response)

# get channel_secret and channel_access_token from your environment variable
channel_secret = "e37fb3dbdef6a04f07cded58e3333f38"
channel_access_token = "IlQKA+p8nuk2tQWFI2rAUmIT/6Eewpse8o3wtSY3g0vqmO9XiygI+UlnsxvpwDqQL1DpmHQ3mS0YvIOmSQkeqohdLzs1JYGiwERQ9hi/k9NP0wQJvSlpJ1o8NqbXyXudoHodBOFCvlWR/jNnIhnYXgdB04t89/1O/w1cDnyilFU="
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

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
        if not isinstance(event.message, TextMessage):
            continue

        text = event.message.text
        userId = event.source.sender_id
        profile = line_bot_api.get_profile(userId)

        if text.startswith("e "):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="@" + profile.display_name + ": " + event.message.text)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=str(english_bot.get_response(text[2:])))
            )

        #line_bot_api.push_message( userId, TextSendMessage(text='push yo, ' + profile.display_name))

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=80, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
