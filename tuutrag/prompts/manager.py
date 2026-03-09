from pathlib import Path
from jinja2 import Environment, FileSystemLoader, meta


TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_prompt(template_name: str, **kwargs) -> dict[str, str]:
    """
    Load a Jinja2 prompt template and render it.

    Args:
        template_name: Filename of the template (e.g. "chunking.j2").
        **kwargs:      Any variables the template needs at render time.

    Returns:
        A dict with "system" and "user" keys containing the rendered strings.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        comment_start_string="{#---",
        comment_end_string="---#}",
    )

    template = env.get_template(template_name)
    module = template.make_module(vars=kwargs)

    return {
        "system": str(module.system).strip(),
        "user": str(module.user).strip(),
    }