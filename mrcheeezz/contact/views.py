from django.views.generic import TemplateView

from .models import Contact

from mrcheeezz import env


class contact(TemplateView):
  template_name = 'contact.html'
    
  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)
    context['contact'] = Contact.objects.all()
    context['border_glow'] = env.border_glow
    context['active_page'] = 'contact'
    context['more'] = False
    context['blocks'] = True

    return context
