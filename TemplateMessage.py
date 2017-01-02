from linebot.models import (
        SendMessage
)

class TemplateMessage(SendMessage):
    def __init__(self, id=None, text=None, actions=None, **kwargs):
        super(TemplateMessage, self).__init__(id=id, **kwargs)

        self.type = 'template'
        self.text = text
        self.actions = actions


class ConfirmTemplateMessage(TemplateMessage):
    def __init__(self, id=None, **kwargs):
        super(ConfirmTemplateMessage, self).__init__(id=id, **kwargs)

        self.template = 'confirm'

class Action():
    def __init__(self, label=None):
        self.label = label

class PostBackAction(Action):
    def __init__(self, label=None, data=None):
        super(PostBackAction, self).__init__(label=label)
        self.type = 'postback'
        self.data = data

class UriAction(Action):
    def __init__(self, label=None, uri=None):
        super(PostBackAction, self).__init__(label=label)
        self.type = 'postback'
        self.uri = uri

class MessageAction(Action):
    def __init__(self, label=None, text=None):
        super(PostBackAction, self).__init__(label=label)
        self.type = 'message'
        self.text = text

