"""Adds an input tape to a state machine."""

class InputTape:
    def __init__(self, stream=None, **kw_args):
        super().__init__(**kw_args)

        assert stream != None

        self.stream = stream
        self._symbol = ''
        self.pos = 0
        self.advance()
        self.pos = 0

    @property
    def symbol(self):
        """Return the current symbol"""
        return self._symbol
    def advance(self):
        """Advance the stream position"""
        self._symbol = self.stream.read(1)
        self.pos += 1
        return self._symbol

    def accept_test(self):
        if self._symbol != '':
            return False
        return super().accept_test()

