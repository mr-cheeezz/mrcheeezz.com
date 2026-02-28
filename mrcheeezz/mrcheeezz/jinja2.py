from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def environment(**options):
    project_root = Path(__file__).resolve().parents[2]
    options.update({
        'loader': FileSystemLoader(str(project_root / 'templates')),
        'autoescape': select_autoescape(['html', 'xml']),
    })
    env = Environment(**options)
    return env
