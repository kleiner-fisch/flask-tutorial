

'''used when the user provides invalid input. -->  causes the offending player to lose
ValueError is only used for internal incorrect data'''
class InvalidUserInputError(Exception):
    """Still an exception raised when uncommon things happen"""
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload # you could add more args
    def __str__(self):
        return str(self.message)