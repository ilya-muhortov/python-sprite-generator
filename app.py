
import os
import click
import datetime

from cerberus import Validator
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from tohtml.config import Config, DefaultConfig
from tohtml.utils import YAMLFile, ImageSize, process_image, RealPath, CustomSprite

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

config = Config()
config.from_object(DefaultConfig)
config.update({
    'BASE_DIR': BASE_DIR,
    'IMAGE_LOCAL_DIR': os.path.join(BASE_DIR, 'data/images_default'),
    'IMAGE_TEMP_DIR': os.path.join(BASE_DIR, 'data/images_temp'),
    'TEMPLATES_DIR': os.path.join(BASE_DIR, 'templates')
})


@click.command()
@click.argument('file_data', type=YAMLFile)
@click.option('--html_template', default=config.DEFAULT_TEMPLATE, required=True, help='HTML template')
@click.option('--output_html_dir', type=click.Path(resolve_path=True, exists=True), required=True)
@click.option('--output_css_dir', type=click.Path(resolve_path=True, exists=True), required=True)
@click.option('--output_sprite_dir', type=click.Path(resolve_path=True, exists=True), required=True)
@click.option('--sprite_url', default=config.SPRITE_URL, required=True)
@click.option('--image_quality', default=config.IMAGE_QUALITY, required=True, help='Image quality')
@click.option('--image_thumb_size', default=config.IMAGE_THUMB_SIZE, type=ImageSize, required=True)
@click.option('--image_local_dir', default=config.IMAGE_LOCAL_DIR, type=click.Path(exists=True), required=True)
@click.option('--image_temp_dir', default=config.IMAGE_TEMP_DIR, type=RealPath(resolve_path=True), required=True)
@click.option('--success_rate', type=click.IntRange(0, 100), default=config.SUCCESS_RATE, required=True)
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def application(ctx, file_data, html_template, output_html_dir, output_css_dir, output_sprite_dir, sprite_url,
                image_quality, image_thumb_size, image_local_dir, image_temp_dir, success_rate, debug):

    jinja_env = Environment(loader=FileSystemLoader(config.TEMPLATES_DIR))
    try:
        template = jinja_env.get_template(html_template)
    except TemplateNotFound as e:
        click.echo('Template %s does not exist.' % html_template)
        exit()

    v = Validator(config.SCHEMA)
    total, success = 0, 0
    sprite_images = []

    n = 0
    sprite_groups = []
    for group, items in file_data.items():
        sprite_images = []
        if isinstance(items, (list, tuple)):
            total += len(items)
            i = 0
            while i < len(items):
                item = items[i]
                if v.validate(item):
                    try:
                        thumb_image = process_image(item['image'], str(n), image_thumb_size,
                                                    image_quality, image_local_dir, image_temp_dir)
                        item['thumb'] = thumb_image
                        item['n'] = n
                        sprite_images.append(thumb_image)
                        i += 1

                    except Exception as e:
                        del items[i]
                        click.echo('Link: %s\nImage: %s\nError: %s\n' % (item['text'], item['image'], e))

                else:
                    del items[i]

                n += 1

            success += len(items)
        sprite_groups.append(sprite_images)

    current_rate = success * 100 / total

    if current_rate >= success_rate:
        for i, sprite_group in enumerate(sprite_groups):
            sprite = CustomSprite(
                sprite_group,
                sprite_name='sprite-%d.png' % i,
                sprite_path=output_sprite_dir,
                css_path=output_css_dir,
                sprite_url=sprite_url,
                class_name='%s-%d' % (config.SPRITE_CLASS_NAME, i),
                overwrite_css=not bool(i)
            )
            sprite.gen_sprite()

        f = open(os.path.join(output_html_dir, 'rendered.html'), 'w')
        html = template.render({
            'data': file_data,
            'date': datetime.datetime.now()
        })
        f.write(html.encode('utf-8'))
        f.close()

        for image in sprite_images:
            os.remove(image)

        click.echo('Success. Current rate is %d%% (%d/%d).' % (current_rate, total, success))
    else:
        click.echo('Current rate is %d%% (%d/%d). Need %s%%.' % (current_rate, total, success, success_rate))


if __name__ == '__main__':
    application()