from django.shortcuts import render
from taggit.models import Tag
from blog.models import Post

def tagged(request):
    query = request.GET.get('tag')
    search = request.GET.get('search')
    if query:
        try:
            tag = Tag.objects.get(name__iexact=query)
            posts = Post.objects.filter(tags=tag)
        except Tag.DoesNotExist:
            tag = None
            posts = Post.objects.none()
    else:
        tag = None
        posts = Post.objects.none()

    context = {
        'tag': tag,
        'posts': posts,
        'q': query,
        'no_search': search,
    }

    return render(request, 'tags/tags_search.html', context)
