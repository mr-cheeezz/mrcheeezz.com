from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def _normalize_relpath(value):
    if not value:
        return None
    return str(value).lstrip("/").replace("\\", "/")


def _collect_referenced_media_paths():
    # Imported lazily so command still loads before app registry is ready.
    from blog.models import Post
    from home.models import Home, Social
    from projects.models import Project
    from specs.models import Spec
    from upload.models import ImageUpload

    referenced = set()

    query_map = [
        (Post, "cover_image"),
        (Home, "pfp"),
        (Social, "svg"),
        (Project, "image"),
        (Spec, "pic"),
        (Spec, "pic2"),
        (ImageUpload, "image"),
    ]

    for model, field_name in query_map:
        for value in model.objects.exclude(**{f"{field_name}__isnull": True}).values_list(field_name, flat=True):
            normalized = _normalize_relpath(value)
            if normalized:
                referenced.add(normalized)

    return referenced


def _collect_generated_deletions():
    static_root = Path(settings.PROJECT_ROOT) / "static"
    gen_root = static_root / "gen"
    if not gen_root.exists():
        return [], []

    keep_prefixes = (
        "css/base.",
        "scripts/blog.",
        "scripts/typewriter.",
        "scripts/bundle.",
    )
    keep_exact = {
        "css/base.css",
        "scripts/blog.js",
        "scripts/typewriter.js",
        "scripts/bundle.js",
    }

    delete_files = []
    for file_path in gen_root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(gen_root).as_posix()
        if rel in keep_exact:
            continue
        if any(rel.startswith(prefix) for prefix in keep_prefixes):
            continue
        else:
            delete_files.append(file_path)

    delete_dirs = [
        p for p in sorted(gen_root.rglob("*"), key=lambda x: len(x.parts), reverse=True) if p.is_dir()
    ]
    return delete_files, delete_dirs


def _collect_media_deletions():
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        return [], []

    referenced = _collect_referenced_media_paths()
    managed_prefixes = {"avatar/", "icons/", "posts/", "projects/", "specs/"}

    delete_files = []
    for file_path in media_root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(media_root).as_posix()
        is_managed = "/" not in rel or any(rel.startswith(prefix) for prefix in managed_prefixes)
        if is_managed and rel not in referenced:
            delete_files.append(file_path)

    delete_dirs = [
        p for p in sorted(media_root.rglob("*"), key=lambda x: len(x.parts), reverse=True) if p.is_dir()
    ]
    return delete_files, delete_dirs


class Command(BaseCommand):
    help = "Delete unused generated/static files and unreferenced media files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually delete files. Without this flag, command runs in dry-run mode.",
        )
        parser.add_argument(
            "--skip-generated",
            action="store_true",
            help="Skip cleanup under static/gen.",
        )
        parser.add_argument(
            "--skip-media",
            action="store_true",
            help="Skip cleanup under MEDIA_ROOT.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Max number of file paths to print in preview output.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        limit = max(options["limit"], 0)

        file_targets = []
        dir_targets = []

        if not options["skip_generated"]:
            files, dirs = _collect_generated_deletions()
            file_targets.extend(files)
            dir_targets.extend(dirs)

        if not options["skip_media"]:
            files, dirs = _collect_media_deletions()
            file_targets.extend(files)
            dir_targets.extend(dirs)

        unique_files = sorted(set(file_targets))
        unique_dirs = sorted(set(dir_targets), key=lambda x: len(x.parts), reverse=True)

        mode = "APPLY" if apply_changes else "DRY-RUN"
        self.stdout.write(self.style.WARNING(f"[{mode}] files matched: {len(unique_files)}"))

        for path in unique_files[:limit]:
            self.stdout.write(f"- {path}")
        if len(unique_files) > limit:
            self.stdout.write(f"... and {len(unique_files) - limit} more")

        if not apply_changes:
            self.stdout.write(self.style.NOTICE("No files deleted. Re-run with --apply to execute."))
            return

        deleted_files = 0
        for file_path in unique_files:
            if file_path.exists():
                file_path.unlink()
                deleted_files += 1

        deleted_dirs = 0
        for dir_path in unique_dirs:
            if dir_path.exists():
                try:
                    dir_path.rmdir()
                    deleted_dirs += 1
                except OSError:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Deleted files: {deleted_files}"))
        self.stdout.write(self.style.SUCCESS(f"Deleted empty dirs: {deleted_dirs}"))
