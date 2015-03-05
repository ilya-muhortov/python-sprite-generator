
import os
import re
import requests
import click
import yaml
from yaml.parser import ParserError
from PIL import Image, ImageOps
from StringIO import StringIO
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class YAMLFileParamType(click.File):

    name = 'yaml'

    def convert(self, value, param, ctx):
        f = super(YAMLFileParamType, self).convert(value, param, ctx)
        try:
            y = yaml.load(f.read())
            data = dict(y)
            if not bool(len(data)):
                raise ValueError

            return data

        except ValueError:
            self.fail('%s is not a yaml file or file is empty' % value, param, ctx)

        except ParserError as e:
            self.fail('%s is wrong yaml format. %s' % (value, str(e).decode('utf-8', 'ignore')), param, ctx)

YAMLFile = YAMLFileParamType()


class ImageSizeParamType(click.ParamType):

    name = 'image_size'

    def convert(self, value, param, ctx):
        value = super(ImageSizeParamType, self).convert(value, param, ctx)
        try:
            size = value.split('x')
            return int(size[0]), int(size[1])
        except (IndexError, ValueError) as e:
            self.fail('Image size format %s error' % value, param, ctx)

ImageSize = ImageSizeParamType()


class RealPathParamType(click.Path):

    def __init__(self, *args, **kwargs):
        self.makedirs = kwargs.pop('makedirs', True)

        super(RealPathParamType, self).__init__(*args, **kwargs)

    def convert(self, value, param, ctx):
        rv = value
        if self.resolve_path:
            rv = os.path.realpath(rv)

        if not os.path.isdir(rv) and self.makedirs:
            os.makedirs(rv)

        return super(RealPathParamType, self).convert(value, param, ctx)

RealPath = RealPathParamType


def process_image(image_path, filename, thumb_size, quality, local_dir, temp_dir):
    is_local = True

    if re.match(r'^https?://', image_path):
        is_local = False
        ext = os.path.splitext(image_path.split('/')[-1])[1]
        r = requests.get(image_path, timeout=10)
        i = Image.open(StringIO(r.content))

    else:
        if not image_path.startswith('/'):
            image_path = os.path.join(local_dir, image_path)

        ext = os.path.splitext(image_path)[1]
        i = Image.open(image_path)

    saved_image_path = os.path.join(temp_dir, '%s%s' % (filename, ext))
    width, height = i.size

    if width > thumb_size[0] or height > thumb_size[1]:
        i = ImageOps.fit(i, thumb_size, Image.ANTIALIAS)
        i.save(saved_image_path, quality=quality)
    elif not is_local:
        i.save(saved_image_path, quality=quality)
    else:
        i.save(saved_image_path, quality=quality)

    return saved_image_path
