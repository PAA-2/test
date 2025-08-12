from datetime import date

DEFAULT_WEIGHTS = {"delay": 2, "priority": 1, "status": 1, "pdca": 1}


def _get_j(action):
    j = action.j
    if j is None and action.delais:
        j = (action.delais - date.today()).days
    return j


def score_priority(action):
    mapping = {"High": 3, "Med": 2, "Low": 1}
    return mapping.get(action.priorite, 0)


def score_delay(action):
    j = _get_j(action)
    if j is None:
        return 0
    if j < 0:
        return 5 + min(10, abs(j) // 7)
    if 0 <= j <= 3:
        return 3
    return 0


def score_status(action):
    if action.statut == "En cours":
        return 2
    if action.statut == "En traitement":
        return 1
    return 0


def score_pdca(action):
    if (action.p or action.d) and not (action.c and action.a):
        return 1
    return 0


def compute_score(action, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    delay = score_delay(action)
    priority = score_priority(action)
    status = score_status(action)
    pdca = score_pdca(action)
    total = (
        delay * weights["delay"]
        + priority * weights["priority"]
        + status * weights["status"]
        + pdca * weights["pdca"]
    )
    return total, {"delay": delay, "priority": priority, "status": status, "pdca": pdca}


def candidate_for_closure(action):
    j = _get_j(action)
    if action.statut not in {"En cours", "En traitement"}:
        return False
    if action.date_realisation:
        return True
    if j is not None and j >= 0 and action.p and action.d:
        return True
    return False

