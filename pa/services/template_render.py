from django.template import engines

from ..models import Template


def render_template(template: Template, context: dict) -> dict:
    django_engine = engines["django"]
    subject_template = django_engine.from_string(template.subject or "")
    body_html_template = django_engine.from_string(template.body_html or "")
    body_text_template = django_engine.from_string(template.body_text or "")
    return {
        "subject": subject_template.render(context),
        "body_html": body_html_template.render(context),
        "body_text": body_text_template.render(context),
    }
