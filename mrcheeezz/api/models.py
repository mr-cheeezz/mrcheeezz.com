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


IMG_VIDEO_PATTERN = r'\[img\s*\(((?:https?://)?[^\)]+)\)\s*\{([^\}]+)\}(\s*\|\s*\(((?:https?://)?[^\)]+)\)\s*\{([^\}]+)\})?\s*img\]'

class SpotifyUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    spotify_user_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()

    class Meta:
        unique_together = ['user_id', 'spotify_user_id']


class APICredential(models.Model):
    PROVIDER_SPOTIFY = "spotify"
    PROVIDER_SPOTIFY_OWNER = "spotify_owner"
    PROVIDER_TWITCH = "twitch"
    PROVIDER_ROBLOX = "roblox"
    PROVIDER_DISCORD = "discord"
    PROVIDER_STEAM = "steam"
    PROVIDER_CHOICES = [
        (PROVIDER_SPOTIFY, "Spotify"),
        (PROVIDER_SPOTIFY_OWNER, "Spotify (Owner)"),
        (PROVIDER_TWITCH, "Twitch"),
        (PROVIDER_ROBLOX, "Roblox"),
        (PROVIDER_DISCORD, "Discord"),
        (PROVIDER_STEAM, "Steam"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, unique=True)
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.TextField(blank=True)
    redirect_uri = models.TextField(blank=True)
    config = models.JSONField(default=dict, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} credential"

class ImageVideoProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("div")

        figure1 = etree.SubElement(el, "figure")
        if m.group(1).endswith(('.png', '.jpg', '.jpeg')):
            img = etree.SubElement(figure1, 'img')
            img.set('src', m.group(1))
            img.set("height", "500")
            img.set("class", "Images")
            img.set("alt", m.group(2)) 
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



class APIDocumentation(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()
    date = models.DateTimeField(default=timezone.now)

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
                   f'<code class=" language-{lang}">' \
                   f'{code}' \
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
        preprocessed_body = APIDocumentation.preprocess_md(self.body)
        md_instance = markdown.Markdown(extensions=['toc', 'tables', 'abbr', 'fenced_code', ImageVideoExtension()])
        html_content = md_instance.convert(preprocessed_body)
        return mark_safe(html_content)

    def body_as_plain_text(self):
        html_content = md(self.body)
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"API Documentation by {self.author.username}" if self.author else "API Documentation"
