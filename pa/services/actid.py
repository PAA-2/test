from pa.models import Action


def generate_act_id() -> str:
    """Return the next ACT identifier in the sequence ACT-0001, ACT-0002, ..."""
    last_action = Action.objects.order_by('id').last()
    if not last_action or not last_action.act_id:
        next_number = 1
    else:
        try:
            last_number = int(last_action.act_id.split('-')[1])
        except (IndexError, ValueError):
            next_number = 1
        else:
            next_number = last_number + 1
    return f"ACT-{next_number:04d}"
