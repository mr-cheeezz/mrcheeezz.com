from django import forms
from django.apps import apps
from django.utils.text import slugify
from bots.models import Bot, BotInstance
from specs.models import Part, Spec


class PartAdminForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ("part", "part_name")
        widgets = {
            "part": forms.TextInput(attrs={"placeholder": "CPU, GPU, RAM, etc."}),
            "part_name": forms.TextInput(attrs={"placeholder": "AMD Ryzen 7 7800X3D"}),
        }


class SpecAdminForm(forms.ModelForm):
    parts_table = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "placeholder": (
                    "CPU|AMD Ryzen 7 7800X3D\n"
                    "GPU|NVIDIA RTX 4070 Ti Super\n"
                    "RAM|32GB DDR5 6000"
                ),
            }
        ),
        help_text=(
            "One part per line using `Part|Part Name` format. "
            "Example: `CPU|AMD Ryzen 7 7800X3D`"
        ),
        label="Parts Table",
    )

    class Meta:
        model = Spec
        fields = (
            "name",
            "slug",
            "icon",
            "parts_table",
            "pic",
            "pic_alt",
            "pic2",
            "pic2_alt",
            "pic_count",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Main Gaming PC"}),
            "slug": forms.TextInput(attrs={"placeholder": "main-gaming-pc (optional)"}),
            "icon": forms.TextInput(attrs={"placeholder": "microchip"}),
            "pic_alt": forms.TextInput(attrs={"placeholder": "Front angle of setup"}),
            "pic2_alt": forms.TextInput(attrs={"placeholder": "Inside case view"}),
        }
        help_texts = {
            "icon": "Font Awesome icon name without the `fa-` prefix.",
            "pic_count": "Optional numeric counter for legacy display logic.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            lines = [
                f"{part.part}|{part.part_name}"
                for part in self.instance.parts.all().order_by("part", "part_name")
            ]
            self.fields["parts_table"].initial = "\n".join(lines)

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        if slug:
            return slug
        name = self.cleaned_data.get("name") or ""
        return slugify(name)

    def clean_parts_table(self):
        raw = (self.cleaned_data.get("parts_table") or "").strip()
        if not raw:
            return []

        parsed_rows = []
        errors = []
        for idx, line in enumerate(raw.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if "|" not in stripped:
                errors.append(f"Line {idx}: missing `|` separator.")
                continue

            part, part_name = [v.strip() for v in stripped.split("|", 1)]
            if not part or not part_name:
                errors.append(f"Line {idx}: both Part and Part Name are required.")
                continue

            parsed_rows.append((part, part_name))

        if errors:
            raise forms.ValidationError(errors)

        return parsed_rows

    def save(self, commit=True):
        spec = super().save(commit=commit)
        parsed_rows = self.cleaned_data.get("parts_table", [])
        if not spec.pk:
            spec.save()

        part_ids = []
        for part, part_name in parsed_rows:
            obj, _ = Part.objects.get_or_create(part=part, part_name=part_name)
            part_ids.append(obj.pk)

        spec.parts.set(part_ids)
        return spec


class BotAdminForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = ("title", "slug", "github_repo")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "FeelsWeirdBot"}),
            "slug": forms.TextInput(attrs={"placeholder": "feelsweirdbot (optional)"}),
            "github_repo": forms.URLInput(attrs={"placeholder": "https://github.com/user/repo"}),
        }

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        if slug:
            return slug
        title = self.cleaned_data.get("title") or ""
        return slugify(title)


class BotInstanceAdminForm(forms.ModelForm):
    class Meta:
        model = BotInstance
        fields = (
            "bot",
            "name",
            "streamer_display",
            "streamer",
            "website_name",
            "website",
            "out_of_commission",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Mr_Cheeezz Main Instance"}),
            "streamer_display": forms.TextInput(attrs={"placeholder": "Mr_Cheeezz"}),
            "streamer": forms.TextInput(attrs={"placeholder": "mr_cheeezz"}),
            "website_name": forms.TextInput(attrs={"placeholder": "Dashboard"}),
            "website": forms.URLInput(attrs={"placeholder": "https://bot.example.com"}),
        }
        help_texts = {
            "streamer": "Lowercase Twitch username used in generated links.",
            "website": "Optional external bot website for this instance.",
        }


MODEL_FORM_MAP = {
    ("specs", "part"): PartAdminForm,
    ("specs", "spec"): SpecAdminForm,
    ("bots", "bot"): BotAdminForm,
    ("bots", "botinstance"): BotInstanceAdminForm,
}


def get_model_form_class(app_name, model_name):
    form_class = MODEL_FORM_MAP.get((app_name.lower(), model_name.lower()))
    if form_class:
        return form_class

    class DynamicModelForm(forms.ModelForm):
        class Meta:
            model = apps.get_model(app_name, model_name)
            fields = "__all__"

    return DynamicModelForm
