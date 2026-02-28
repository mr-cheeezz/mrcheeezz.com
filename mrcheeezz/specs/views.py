from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import Spec

class specs_list(TemplateView):
  template_name = 'specs/list.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)
    context['specs'] = Spec.objects.all().order_by('created_at')
    context['active_page'] = 'specs'
    context['more'] = True

    return context
  
class specs_detail(TemplateView):
  template_name = 'specs/base.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)
    spec = get_object_or_404(Spec, slug=self.kwargs['slug'])
    try:
      next_spec = spec.get_next_by_created_at()
    except Spec.DoesNotExist:
      next_spec = None

    try:
      previous_spec = spec.get_previous_by_created_at()
    except Spec.DoesNotExist:
      previous_spec = None

    context['specs'] = spec
    context['parts'] = spec.parts.all()
    context['next_spec'] = next_spec
    context['previous_spec'] = previous_spec
    context['active_page'] = 'specs'
    context['more'] = True

    return context
