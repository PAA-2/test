from __future__ import annotations

import re
from typing import Any, Dict

from django.core.exceptions import ValidationError

from .models import CustomField, Profile


ROLE_VIS_MAP = {
    Profile.Role.SUPER_ADMIN: {"All", "SA_PP", "Pilote", "Utilisateur"},
    Profile.Role.PILOTE_PROCESSUS: {"All", "SA_PP", "Pilote", "Utilisateur"},
    Profile.Role.PILOTE: {"All", "Pilote", "Utilisateur"},
    Profile.Role.UTILISATEUR: {"All", "Utilisateur"},
}


def load_definitions_for_role(user) -> Dict[str, CustomField]:
    if not user or not user.is_authenticated:
        return {}
    role = getattr(user.profile, "role", None)
    visibilities = ROLE_VIS_MAP.get(role, {"All"})
    defs = (
        CustomField.objects.filter(active=True, role_visibility__in=visibilities)
        .prefetch_related("options")
        .all()
    )
    return {cf.key: cf for cf in defs}


def _validate_value(cf: CustomField, value: Any):
    if cf.type == CustomField.Type.TEXT:
        if not isinstance(value, str):
            raise ValidationError("must be a string")
        if cf.min is not None and len(value) < cf.min:
            raise ValidationError("too_short")
        if cf.max is not None and len(value) > cf.max:
            raise ValidationError("too_long")
        if cf.regex and not re.fullmatch(cf.regex, value):
            raise ValidationError("invalid_format")
    elif cf.type == CustomField.Type.NUMBER:
        if not isinstance(value, (int, float)):
            raise ValidationError("must_be_number")
        if cf.min is not None and value < cf.min:
            raise ValidationError("min_value")
        if cf.max is not None and value > cf.max:
            raise ValidationError("max_value")
    elif cf.type == CustomField.Type.DATE:
        if not isinstance(value, str):
            raise ValidationError("must_be_iso_date")
        # basic ISO date check
        try:
            from datetime import date

            date.fromisoformat(value)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValidationError("invalid_date") from exc
    elif cf.type == CustomField.Type.SELECT:
        allowed = {o.value for o in cf.options.all()}
        if value not in allowed:
            raise ValidationError("invalid_choice")
    elif cf.type == CustomField.Type.TAGS:
        if not isinstance(value, list):
            raise ValidationError("must_be_list")
        allowed = {o.value for o in cf.options.all()}
        invalid = [v for v in value if v not in allowed]
        if invalid:
            raise ValidationError("invalid_choice")
    elif cf.type == CustomField.Type.BOOL:
        if not isinstance(value, bool):
            raise ValidationError("must_be_bool")


def validate_custom_payload(payload: Dict[str, Any], defs: Dict[str, CustomField]) -> Dict[str, Any]:
    errors = {}
    clean = {}
    for key, cf in defs.items():
        if key not in payload:
            if cf.required:
                errors[key] = "required"
            continue
        value = payload.get(key)
        try:
            _validate_value(cf, value)
            clean[key] = value
        except ValidationError as exc:
            errors[key] = exc.message
    # Ignore keys not in defs
    if errors:
        raise ValidationError(errors)
    return clean


def filter_custom_for_role(data: Dict[str, Any], user) -> Dict[str, Any]:
    defs = load_definitions_for_role(user)
    return {k: v for k, v in data.items() if k in defs}
