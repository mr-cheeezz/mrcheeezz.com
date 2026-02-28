from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from .forms import get_model_form_class

included_apps = ['home', 'about', 'contact', 'projects', 'specs', 'bots', 'blog']

@user_passes_test(lambda u: u.is_superuser)
def app_models(request, app_name):
    app = apps.get_app_config(app_name)
    content_types = ContentType.objects.filter(app_label=app_name)
    models = [{'model_name': content_type.model} for content_type in content_types]
    if app_name == 'home':
        models = [model for model in models if model['model_name'] != 'social']
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

    return render(request, 'admin/models/models.html', {'apps': True, 'app_names': app_names, 'app_name': app_name, 'models': models})

@user_passes_test(lambda u: u.is_superuser)
def model_instances(request, app_name, model_name):
    if app_name == 'home' and model_name == 'social':
        return redirect(reverse('custom_admin:socials_home'))

    app = apps.get_app_config(app_name)
    model = apps.get_model(app.label, model_name)
    instances = model.objects.all()
    if hasattr(model, "title"):
        instances = instances.order_by("title")
    elif hasattr(model, "name"):
        instances = instances.order_by("name")
    elif hasattr(model, "part"):
        instances = instances.order_by("part", "part_name")
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

    instance_rows = []
    for instance in instances:
        summary = ""
        model_key = model_name.lower()
        if app_name == "specs" and model_key == "spec":
            summary = f"{instance.parts.count()} part(s) • icon: fa-{instance.icon}"
        elif app_name == "specs" and model_key == "part":
            summary = f"{instance.part} • {instance.part_name}"
        elif app_name == "bots" and model_key == "bot":
            summary = f"{instance.type_list.count()} instance(s)"
        elif app_name == "bots" and model_key == "botinstance":
            status = "Out of commission" if instance.out_of_commission else "Active"
            summary = f"{instance.streamer_display} • {status}"
        instance_rows.append({"instance": instance, "summary": summary})

    return render(
        request,
        'admin/models/instances.html',
        {
            'apps': True,
            'app_name': app_name,
            'model_name': model_name,
            'app_names': app_names,
            'instances': instances,
            'instance_rows': instance_rows,
        },
    )

@user_passes_test(lambda u: u.is_superuser)
def delete_instance(request, app_name, model_name, pk):
    app = apps.get_app_config(app_name)
    model = apps.get_model(app.label, model_name)
    instance = get_object_or_404(model, pk=pk)
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

    if request.method == 'POST':
        instance.delete()
        return redirect(reverse('custom_admin:model_instances', kwargs={'app_name': app_name, 'model_name': model_name}))

    return render(request, 'admin/models/delete.html', {'apps': True, 'app_names': app_names, 'instance': instance, 'app_name': app_name, 'model_name': model_name})

@user_passes_test(lambda u: u.is_superuser)
def add_instance(request, app_name, model_name):
    app = apps.get_app_config(app_name)
    model = apps.get_model(app.label, model_name)
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

    form_class = get_model_form_class(app_name, model_name)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('custom_admin:model_instances', kwargs={'app_name': app_name, 'model_name': model_name}))
    else:
        form = form_class()

    return render(request, 'admin/models/add.html', {'apps': True, 'app_names': app_names, 'form': form, 'app_name': app_name, 'model_name': model_name})

@user_passes_test(lambda u: u.is_superuser)
def edit_instance(request, app_name, model_name, pk):
    app = apps.get_app_config(app_name)
    model = apps.get_model(app.label, model_name)
    instance = get_object_or_404(model, pk=pk)
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]


    form_class = get_model_form_class(app_name, model_name)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('custom_admin:model_instances', kwargs={'app_name': app_name, 'model_name': model_name}))
    else:
        form = form_class(instance=instance)

    return render(request, 'admin/models/edit.html', {'apps': True, 'app_names': app_names, 'form': form, 'app_name': app_name, 'model_name': model_name, 'instance': instance})
