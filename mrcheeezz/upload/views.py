import os
import shutil

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic.edit import DeleteView
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import ImageUploadForm
from .models import ImageUpload

class UploadImage(View):
    def get(self, request):
        form = ImageUploadForm()
        context = {
            'form': form,
            'active_page': 'upload',
            'more': True,
        }
        return render(request, 'upload/upload.html', context)

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img_upload = form.save()

            temp_path = os.path.join(settings.MEDIA_ROOT, img_upload.image.name)
            new_path = os.path.join('/home/images/p/', os.path.basename(img_upload.image.name))
            shutil.copy(temp_path, new_path)

            img_upload.image_path = os.path.join('/p/', os.path.basename(img_upload.image.name))
            img_upload.save()

            return redirect('upload_success', img_id=img_upload.id)

        context = {
            'form': form,
            'active_page': 'upload',
            'more': True,
        }
        return render(request, 'upload/upload.html', context)

class UploadSuccess(View):
    def get(self, request, img_id):
        img_upload = get_object_or_404(ImageUpload, id=img_id)
        return render(request, 'upload/success.html', {'upload': img_upload})

class DeleteUpload(DeleteView):
    model = ImageUpload
    success_url = reverse_lazy('upload')
    template_name = 'upload/delete.html'

    def get_object(self, queryset=None):
        img_id = self.kwargs.get('pk')
        return get_object_or_404(ImageUpload, id=img_id)

    def delete(self, request, *args, **kwargs):
        img_upload = self.get_object()
        img_path = os.path.join('/home/images/p/', os.path.basename(img_upload.image.name))

        if os.path.exists(img_path):
            os.remove(img_path)

        return super().delete(request, *args, **kwargs)