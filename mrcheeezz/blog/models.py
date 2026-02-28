from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
from django.utils.safestring import mark_safe
from markdown import markdown as md, util
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup
import re
import html
import random
import string
import base64


def name_to_base64(name):
    return base64.b64encode(name.encode()).decode('utf-8')


def random_string(length=25):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def upload_to_random_path(instance, filename):
    extension = filename.split('.')[-1]
    encoded_name = name_to_base64(instance.name)
    return 'posts/{encoded_name}/{new_name}.{ext}'.format(encoded_name=encoded_name, new_name=random_string(25), ext=extension)


IMG_VIDEO_PATTERN = r'\[img\s*\(((?:https?://)?[^\)]+)\)\s*\{([^\}]+)\}(\s*\|\s*\(((?:https?://)?[^\)]+)\)\s*\{([^\}]+)\})?\s*img\]'


class ImageVideoProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("div")

        figure1 = etree.SubElement(el, "figure")
        if m.group(1).endswith(('.png', '.jpg', '.jpeg')):
            img = etree.SubElement(figure1, 'img')
            img.set('src', m.group(1))
            img.set("height", "500")
            img.set("class", "Images")
            img.set("alt", m.group(2))  # Setting alt attribute
            figure1.set("class", "post-image")
        else:
            video = etree.SubElement(figure1, 'video', controls="true")
            video.set("height", "500")
            source = etree.SubElement(video, 'source')
            source.set('src', m.group(1))
            source.set('type', 'video/mp4')
            figure1.set("class", "post-video")
        figcaption1 = etree.SubElement(figure1, 'figcaption')
        figcaption1.text = m.group(2)

        if m.group(4):
            figure2 = etree.SubElement(el, "figure")
            if m.group(4).endswith(('.png', '.jpg', '.jpeg')):
                img = etree.SubElement(figure2, 'img')
                img.set('src', m.group(4))
                img.set("height", "500")
                img.set("class", "Images")
                img.set("alt", m.group(5))
                figure2.set("class", "post-image")
            else:
                video = etree.SubElement(figure2, 'video', controls="true")
                video.set("height", "500")
                source = etree.SubElement(video, 'source')
                source.set('src', m.group(4))
                source.set('type', 'video/mp4')
                figure2.set("class", "post-video")
            figcaption2 = etree.SubElement(figure2, 'figcaption')
            figcaption2.text = m.group(5)

        return el, m.start(0), m.end(0)


class ImageVideoExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(ImageVideoProcessor(IMG_VIDEO_PATTERN, md), 'img_video', 175)



class Post(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)
    tags = TaggableManager()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    calculated_read_time = models.IntegerField(blank=True, null=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to=upload_to_random_path, blank=True, null=True)
    slug = models.SlugField(max_length=250, unique_for_date='date')

    @staticmethod
    def preprocess_md(md_text):
        pattern = re.compile(r'```(\w+)\[([^\]]+)\]([\s\S]*?)```', re.DOTALL)

        def repl(match):
            lang = match.group(1)
            title = match.group(2)
            code = html.escape(match.group(3).strip())
            id = random.randint(100000000, 999999999)

            return f'<div class="collapsable-code">\n' \
                   f'<input id="{id}" type="checkbox">\n' \
                   f'<label for="{id}">\n' \
                   f'<span class="collapsable-code__language">{lang}</span>\n' \
                   f'<span class="collapsable-code__title">{title}</span>\n' \
                   f'<span class="collapsable-code__toggle"><i class="fas fa-chevron-up toggle-expand"></i><i class="fas fa-chevron-down toggle-collapse"></i></span>\n' \
                   f'</label>\n' \
                   f'<div class="code-toolbar">\n' \
                   f'<pre class=" language-{lang}" tabindex="0">\n' \
                   f'<code class=" language-{lang}">\n' \
                   f'{code}\n' \
                   f'</code>\n' \
                   f'</pre>\n' \
                   f'<div class="toolbar">\n' \
                   f'<div class="toolbar-item">\n' \
                   f'<button class="copy-to-clipboard-button" type="button" data-copy-state="copy">\n' \
                   f'<span>Copy</span>\n' \
                   f'</button>\n' \
                   f'</div>\n' \
                   f'</div>\n' \
                   f'</div>\n' \
                   f'</div>'

        return pattern.sub(repl, md_text)

    def body_as_html(self):
        import markdown
        preprocessed_body = Post.preprocess_md(self.body)
        md_instance = markdown.Markdown(extensions=['toc', 'tables', 'abbr', 'fenced_code', ImageVideoExtension()])
        html_content = md_instance.convert(preprocessed_body)
        return mark_safe(html_content)

    def body_as_plain_text(self):
        html_content = md(self.body)
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return text

    def calculate_read_time(self):
        word_count = len(self.body.split())
        reading_speed = 100.0
        time = word_count / reading_speed
        return round(time)

    def save(self, *args, **kwargs):
        self.calculated_read_time = self.calculate_read_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
