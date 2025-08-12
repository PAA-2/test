"""Utilities for sending Outlook emails via local client."""
from django.conf import settings
from django.template import Context, Template

try:
    import win32com.client  # type: ignore
except Exception:  # pragma: no cover
    win32com = None  # type: ignore


def render_template(template, context):
    ctx = Context(context or {})
    subject = Template(template.subject).render(ctx)
    body_html = Template(template.body_html).render(ctx) if template.body_html else None
    body_text = Template(template.body_text).render(ctx) if template.body_text else None
    return subject, body_html, body_text


def build_mail(to, cc=None, bcc=None, subject="", body_html=None, body_text=None, attachments=None):
    if win32com is None:
        raise RuntimeError("Outlook indisponible sur cet hôte")
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    if to:
        mail.To = ";".join(to)
    if cc:
        mail.CC = ";".join(cc)
    if bcc:
        mail.BCC = ";".join(bcc)
    mail.Subject = subject
    if body_html:
        mail.HTMLBody = body_html
    elif body_text:
        mail.Body = body_text
    else:
        mail.Body = ""
    for path in attachments or []:
        mail.Attachments.Add(path)
    # Signature support (optional placeholder)
    if getattr(settings, "OUTLOOK_SIGNATURE_NAME", None):  # pragma: no cover - best effort
        try:
            sig = getattr(mail, "Signature", None)
            if sig:
                mail.HTMLBody += sig  # naive append
        except Exception:
            pass
    return mail


def send_mail(mail, send=True):
    if send:
        mail.Send()
    else:
        mail.Save()
    return mail
