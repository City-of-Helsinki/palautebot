# originally from http://www.michaelpollmeier.com/python-mock-how-to-assert-a-substring-of-logger-output
class SubstringMatcher:
    """
    This can be used to do "log message contains" assertions
    """
    def __init__(self, containing):
        self.containing = containing.lower()

    def __eq__(self, other):
        return other.lower().find(self.containing) > -1

    def __str__(self):
        return 'a string containing "%s"' % self.containing

    __repr__ = __str__
