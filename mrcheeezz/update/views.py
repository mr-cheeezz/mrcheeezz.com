from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from mrcheeezz import env
from mrcheeezz import version
import os
import markdown
from pathlib import Path


def _static_markdown_path(filename):
    return Path(settings.PROJECT_ROOT) / "static" / "markdown" / filename


def _project_root_path(filename):
    return Path(settings.PROJECT_ROOT) / filename


def _first_existing_source(paths):
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


def _sync_markdown_file(source_path, target_path):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    source_content = source_path.read_bytes()

    if target_path.exists() and not target_path.is_symlink():
        target_content = target_path.read_bytes()
        if target_content == source_content:
            return
    elif target_path.is_symlink():
        target_path.unlink()

    target_path.write_bytes(source_content)


def sync_static_markdown_docs():
    changelog_source = _first_existing_source(
        [
            _project_root_path("CHANGELOG.md"),
            _project_root_path("CHANGELOG"),
        ]
    )
    legal_source = _first_existing_source(
        [
            _project_root_path("LEGAL.md"),
            _project_root_path("LEGAL"),
            _project_root_path("LICENSE.md"),
            _project_root_path("LICENSE"),
        ]
    )

    if changelog_source:
        _sync_markdown_file(changelog_source, _static_markdown_path("changelog.md"))
    if legal_source:
        _sync_markdown_file(legal_source, _static_markdown_path("legal.md"))


def update_log(request):
    sync_static_markdown_docs()
    file_path = _static_markdown_path("changelog.md")

    if not file_path.exists():
        markdown_content = "# Changelog\n\nNo changelog file found."
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

    html_content = markdown.markdown(
        markdown_content,
        extensions=["smarty", "fenced_code", "tables", "sane_lists", "toc"],
    )

    return render(request, 'documents/updates.html', {'html_content': html_content, 'version_verbose': version.verbose_version})

def get_last_modified_time(file_path):
    try:
        last_modified_timestamp = os.path.getmtime(file_path)
        last_modified_time = timezone.datetime.fromtimestamp(last_modified_timestamp)
        return last_modified_time
    except FileNotFoundError:
        return None

def replace_placeholders(content):
    current_year = timezone.now().year
    replaced_content = content.replace("[Year]", str(current_year)).replace("[Name]", env.name)
    replaced_content = replaced_content.replace("[Location]", env.location).replace("[Server]", env.server)
    replaced_content = replaced_content.replace("[Contact]", f'<a href="mailto:{env.email}">{env.pub_email}</a>')
    replaced_content = replaced_content.replace("[Email]", env.pub_email)

    return replaced_content

def copyright(request):
    sync_static_markdown_docs()
    file_path = _static_markdown_path("legal.md")

    if not file_path.exists():
        markdown_content = "# Legal\n\nNo legal file found."
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

    markdown_content = replace_placeholders(markdown_content)

    html_content = markdown.markdown(
        markdown_content,
        extensions=["smarty", "fenced_code", "tables", "sane_lists", "toc"],
    )
    
    last_modified_time = get_last_modified_time(file_path)

    return render(request, 'documents/copyright.html', {'html_content': html_content, 'last_modified_time': last_modified_time})
