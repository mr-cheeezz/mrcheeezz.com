from django.contrib import admin

from .models import Tag, FAQ, Project, InstallInstruction, KnownIssue, Feature

admin.site.register(Tag)
admin.site.register(FAQ)
admin.site.register(InstallInstruction)
admin.site.register(KnownIssue)
admin.site.register(Feature)
admin.site.register(Project)