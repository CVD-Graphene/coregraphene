class BaseCommand(object):
    def __init__(self,
                 command=None,
                 value=None,
                 with_answer=False,
                 repeat=False,
                 on_answer=None,
                 **kwargs,
                 ):
        self.command = command
        self.value = value
        self.with_answer = with_answer
        self.repeat = repeat
        self.on_answer = on_answer
        self.kwargs = kwargs
