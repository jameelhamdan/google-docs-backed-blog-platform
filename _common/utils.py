from django.utils.text import slugify
from .exceptions import EditorJSParseError
import uuid
import random
import string
import json
from bs4 import BeautifulSoup


def random_str(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_uuid(repeat=1):
    final_uuid = ''
    for i in range(0, repeat):
        final_uuid += uuid.uuid4().hex

    return final_uuid


def klass_unique_slug_generator(klass, slug, slug_name='slug', separator='-'):
    qs_exists = klass.objects.filter(**{slug_name: slug}).exists()
    if qs_exists:
        new_slug = f'{slug}{separator}{random_str(4)}'
        return klass_unique_slug_generator(klass, new_slug, slug_name)
    else:
        return slug


def unique_slug_generator(instance, new_slug=None, field_name='title', slug_name='slug'):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title/name character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, field_name))

    return klass_unique_slug_generator(instance.__class__, slug, slug_name)


def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style', 'iframe']):
        script.extract()

    return str(soup)


def parse_editor_js_data(data: str) -> str:
    """
    Tries to parse editor_js data into html and raises EditorJSParseError if doesn't parse correctly
    :param data:
    :return: str
    """
    if data == '':
        return ''

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        raise EditorJSParseError('Couldn\'t Parse data into valid json')

    if not isinstance(data, dict):
        raise EditorJSParseError('Data must be valid dict')

    if 'blocks' not in data.keys():
        raise EditorJSParseError('Data must be have a blocks array')

    blocks_list = data['blocks']
    if not isinstance(blocks_list, list):
        raise EditorJSParseError('block attribute must be an array')

    html = ""
    styles = {
        'header': "ce-header",
    }

    def wrap_block(_html):
        return f"""
        <div class='ce-block'>
            <div class='ce-block__content'>
                {_html}
            </div>
        </div>
        """

    def raise_exp():
        raise EditorJSParseError('block must have type and data attributes')

    for block in blocks_list:
        try:
            block_type, block_data = block['type'], block['data']

            if block_type == 'header':
                level = block_data['level']
                block_style = block_data['level']
                text = block_data['text']
                html += wrap_block(_html=f' <h{level} class="{block_style}"> {text} </h{level}>')

            elif block_type == 'paragraph':
                text = block_data['text']
                html += wrap_block(f'<p class="ce-paragraph cdx-block">{text}</p>')

            elif block_type == 'delimiter':
                html += wrap_block(f'<div class="ce-delimiter cdx-block"></div>')

            elif block_type == 'code':
                code = block_data['code']
                html += wrap_block(f'<pre>f{code}</pre>')

            elif block_type == 'quote':
                text = block_data['text']
                html += wrap_block(f'<blockquote class="cdx-block cdx-quote"><div class="cdx-quote__text"> {text}</div></blockquote>')

            elif block_type in ['rawTool', 'rawHTML', 'raw', 'html']:
                html_data = block_data['html']
                html += wrap_block(f'<div class="cdx-block ce-rawtool"><pre class= ""> {html_data} </pre></div>')
            elif block_type == 'image':
                caption = block_data['caption']
                file_url = block_data['url']

                html += wrap_block(
                    f'''
                    <div class="cdx-block image-tool">
                        <div class="image-tool__image">
                        <div class="image-tool__image-preloader"></div>
                            <img class="image-tool__image-picture" alt="{caption}" src="{file_url}" title="{caption}">
                        </div>
                        <div class="cdx-input image-tool__caption" data-placeholder="Caption">{caption}</div>
                    </div>
                  '''
                )
            elif block_type == 'list':
                style = {
                  'unordered': 'li',
                  'ordered': 'ol'
                }
                items = ''
                block_style = style[block_data['style']]

                if not isinstance(block_data['items'], list):
                    raise_exp()

                for item in block_data['items']:
                    items += f'<{block_style} class="cdx-list__item">{item}</{block_style}>'

                html += wrap_block(
                  f'<ul class="cdx-block cdx-list cdx-list--{block_data["style"]}">{items}</ul>'
                )
            elif block_type == 'table':
                items = ''
                if not isinstance(block_data['content'], list):
                    raise_exp()

                for row in block_data['content']:
                    if not isinstance(row, list):
                        raise_exp()

                    row_items = ''
                    for item in row:
                        row_items += f'<td class="tc-table__cell"><div class="tc-table__area">{item}</div></td>'
                    items += f'<tr>{row_items}</tr>'

                html += wrap_block(
                  f'<div class="cdx-block"><div class="tc-table__wrap"><table class="tc-table ">{items}</table></div></script>'
                )
            else:
                raise_exp()

        except KeyError as e:
            raise EditorJSParseError('block must have type and data attributes')

        except ValueError as e:
            raise EditorJSParseError('block must have type and data attributes')

    return clean_html(html)
