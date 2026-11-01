ALLOWED_PRIORITIES = {"Low", "Medium", "High"}

ALLOWED_CATEGORIES = {
    "Work",
    "Personal",
    "Finance",
    "Security",
    "Promotion",
    "Social",
    "Other",
}


def decide_action(analysis):
    priority = analysis["priority"]
    action_required = analysis["action_required"]

    if priority not in ALLOWED_PRIORITIES:
        return "INVALID_ANALYSIS"

    if analysis["category"] not in ALLOWED_CATEGORIES:
        return "INVALID_ANALYSIS"

    if priority == "High" and action_required:
        return "URGENT_ATTENTION"
    elif action_required:
        return "ACTION_REQUIRED"
    else:
        return "NO_ACTION"
