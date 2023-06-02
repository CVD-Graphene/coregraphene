class BaseActionException(Exception):
    pass


class NotAchievingActionGoal(BaseActionException):
    def __str__(self):
        return f"NotAchievingActionGoal"
