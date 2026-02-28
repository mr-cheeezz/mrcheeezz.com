from django.shortcuts import get_object_or_404, redirect, render

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

from django.core.paginator import Paginator

from django.urls import reverse

from django.http import JsonResponse, Http404
from django.db.utils import OperationalError, ProgrammingError

from django.utils.decorators import method_decorator

from .models import Post
from .forms import PostForm
from settings.models import SiteSetting


def _blog_enabled():
    try:
        setting = SiteSetting.objects.first()
    except (OperationalError, ProgrammingError):
        return True
    return setting.blog_enabled if setting else True


class BlogEnabledMixin:
    def dispatch(self, request, *args, **kwargs):
        if not _blog_enabled():
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class BlogList(BlogEnabledMixin, ListView):
    model = Post
    template_name = 'blog/post-list.html'
    context_object_name = 'blog'
    ordering = ['-date']
    paginate_by = 5 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'blog'

        list_of_posts = Post.objects.all().order_by('-date')
        paginator = Paginator(list_of_posts, self.paginate_by)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        return context


class PostDetail(BlogEnabledMixin, View):
    template_name = 'blog/post.html'
    
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        try:
            next_post = post.get_next_by_date()
        except Post.DoesNotExist:
            next_post = None

        try:
            previous_post = post.get_previous_by_date()
        except Post.DoesNotExist:
            previous_post = None

        context = {
            'post': post,
            'next_post': next_post,
            'previous_post': previous_post,
            'more': False
        }

        return render(request, self.template_name, context)
    
  
@method_decorator(csrf_exempt, name='dispatch')
class DeletePost(UserPassesTestMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not _blog_enabled():
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        context = {
            'error_code': 401,
            'error_message': 'Unauthorized Access',
            'extra_message': "You don't have access to this page.",
        }
        return render(self.request, 'error.html', context, status=401)

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        return JsonResponse({'success': True})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'blog'
        
        return context
    
class EditPost(BlogEnabledMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/edit.html'

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        context = {
            'error_code': 401,
            'error_message': 'Unauthorized Access',
            'extra_message': "You don't have access to this page.",
        }
        return render(self.request, 'error.html', context, status=401)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.slug])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'blog'
        
        return context

class CreatePost(BlogEnabledMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        context = {
            'error_code': 401,
            'error_message': 'Unauthorized Access',
            'extra_message': "You don't have access to this page.",
        }
        return render(self.request, 'error.html', context, status=401)

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        tags = form.cleaned_data['tags']
        self.object.tags.set(*tags)
        return response

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.slug])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'blog'
        
        return context
    
