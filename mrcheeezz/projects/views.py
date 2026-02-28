from django.views.generic import TemplateView
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Project


class ProjectList(ListView):
    model = Project
    template_name = 'projects/project-list.html'
    context_object_name = 'project'
    ordering = '-date'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'projects'
        context['more'] = True

        list_of_posts = Project.objects.all().order_by(self.ordering)
        paginator = Paginator(list_of_posts, self.paginate_by)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        return context

class ProjectDetail(TemplateView):
  template_name = 'projects/project-details.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    project = get_object_or_404(Project, slug=self.kwargs['slug'])
    try:
      next_project = project.get_next_by_date()
    except Project.DoesNotExist:
      next_project = None

    try:
      previous_project = project.get_previous_by_date()
    except Project.DoesNotExist:
      previous_project = None

    context['project'] = project
    context['next_project'] = next_project
    context['previous_project'] = previous_project
    context['active_page'] = 'projects'
    context['more'] = True

    return context

