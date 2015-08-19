
import os


class Config(dict):

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})

    def __getattr__(self, item):
        return self[item]

    def from_object(self, obj):
        """
        Updates the values from the given object. An object may be one on
        the following types:
        - an actual object reference: that object is used directly
        """

        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


class DefaultConfig(object):

    BASE_DIR = None

    IMAGE_LOCAL_DIR = None
    IMAGE_TEMP_DIR = None

    DEFAULT_TEMPLATE = 'default.html'

    IMAGE_THUMB_SIZE = '100x80'
    IMAGE_QUALITY = 85

    SUCCESS_RATE = 100

    REGEX_LINK = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

    SCHEMA = {
        'text': {
            'type': 'string',
            'required': True
        },
        'href': {
            'type': 'string',
            'regex': REGEX_LINK,
            'required': True
        },
        'image': {
            'type': 'string',
            'required': True
        }
    }

    SPRITE_URL = ''
    SPRITE_CLASS_NAME = 'sprite'
