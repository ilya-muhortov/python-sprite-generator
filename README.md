python-tohtml
======
Использование  
python app.py data/example/data.yml \
        --success_rate=80 \
        --output_html_dir=data/rendered \
        --output_css_dir=data/rendered/css/ \
        --image_thumb_size=200x100 \
        --output_sprite_dir=data/rendered/image \
        --sprite_url=../images/  
  
Параметры:  
* html_template - HTML файл шаблона (используется шаблонизатор [jinja](http://jinja.pocoo.org/))  
* output_html_dir - Директория для сохраения сгенерированного html файл
* output_css_dir - Директория для сохраения css файл
* output_sprite_dir - Директория для сохраения спрайта
* sprite_url - URL адрес в css до спрайта
* image_quality - Качество изображения (0 - 100)
* image_thumb_size - Размер изображения (В формате (width)x(height), например 100x80)
* image_local_dir - Папка с локальными изображениями
* success_rate - Процент успешных ссылок, необходимый для генерации шаблона

Requires
-----
  * Cerberus==0.8
  * Jinja2==2.7.3
  * PIL==1.1.7
  * Pillow==2.7.0
  * click==3.3
  * requests==2.5.3
  * six==1.9.0
  * spriter==1.3.0
