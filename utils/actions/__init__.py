def get_action_by_name(name, actions_list):
    for i, action in enumerate(actions_list):
        if action.name.strip() == name:
            return action, i
    return None, 0


def safe_check(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"{str(e)}"
    return wrapper
