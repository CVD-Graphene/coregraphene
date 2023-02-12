class BaseConditionException(Exception):
    def __init__(self, description=None):
        s = description if description is not None else "Condition is not valid"
        super().__init__(s)


class BadNumbersConditionException(BaseConditionException):
    def __init__(self):
        super().__init__("Bad numbers")
