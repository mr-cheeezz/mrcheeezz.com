from django.db import models

import os
import random
import string

def generate_random_filename(instance, filename):
    filename_base = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    extension = os.path.splitext(filename)[1]

    return 'uploads/images/{}{}'.format(filename_base, extension)

class ImageUpload(models.Model):
    image_path = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to=generate_random_filename)

    def __str__(self):
        return self.image_path
