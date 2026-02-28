from pathlib import Path
from shutil import copyfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from rjsmin import jsmin


class Command(BaseCommand):
    help = "Build minified JS files in static/gen/scripts and create versioned aliases."

    SOURCE_FILES = [
        "scripts/menu.js",
        "scripts/theme.js",
        "scripts/prism.js",
        "scripts/nav_typewrite.js",
        "scripts/time.js",
        "scripts/now_playing.js",
        "scripts/discord.js",
    ]

    EXTRA_JS = [
        ("scripts/blog.js", "gen/scripts/blog.js"),
        ("scripts/typewriter.js", "gen/scripts/typewriter.js"),
    ]

    def handle(self, *args, **options):
        static_root = Path(settings.PROJECT_ROOT) / "static"
        output_path = static_root / "gen" / "scripts" / "bundle.js"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        missing = []
        chunks = []

        for rel in self.SOURCE_FILES:
            src = static_root / rel
            if not src.exists():
                missing.append(str(src))
                continue
            chunks.append(src.read_text(encoding="utf-8"))

        if missing:
            raise CommandError(
                "Missing source script files:\n- " + "\n- ".join(missing)
            )

        # Delimit each file to avoid accidental token merge, then minify.
        bundle_text = "\n;\n".join(chunks) + "\n"
        bundle_text = jsmin(bundle_text)
        output_path.write_text(bundle_text, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Built {output_path}"))

        # Create filename-versioned aliases expected by UI URL format:
        # /static/gen/scripts/bundle.<version>.js
        version = str(int(output_path.stat().st_mtime))
        versioned_js = output_path.with_name(f"bundle.{version}.js")
        copyfile(output_path, versioned_js)
        self.stdout.write(self.style.SUCCESS(f"Aliased {versioned_js}"))

        for src_rel, out_rel in self.EXTRA_JS:
            src = static_root / src_rel
            out = static_root / out_rel
            if not src.exists():
                raise CommandError(f"Missing source script file: {src}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(jsmin(src.read_text(encoding="utf-8")), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Built {out}"))
            extra_version = str(int(out.stat().st_mtime))
            versioned_extra = out.with_name(f"{out.stem}.{extra_version}{out.suffix}")
            copyfile(out, versioned_extra)
            self.stdout.write(self.style.SUCCESS(f"Aliased {versioned_extra}"))

        css_base = static_root / "gen" / "css" / "base.css"
        if css_base.exists():
            css_version = str(int(css_base.stat().st_mtime))
            versioned_css = css_base.with_name(f"base.{css_version}.css")
            copyfile(css_base, versioned_css)
            self.stdout.write(self.style.SUCCESS(f"Aliased {versioned_css}"))
