"""Example DFA to read the language (p^n)(q^m)"""

import sys
sys.path.append("../packages")

from pycog.statemachine import *

class PsAndQs(StateMachine):
    def __init__(self, stream):
        super().__init__('p')

        self.stream = stream
        self._symbol = ''
        self.pos = 0
        self.advance()
        self.pos = 0
        self.error_msg = ''

    @property
    def symbol(self):
        """Return the current symbol"""
        return self._symbol
    def advance(self):
        """Advance the stream position"""
        self._symbol = self.stream.read(1)
        self.pos += 1
        return self._symbol

    @state('p')
    def p(self):
        while self.symbol == 'p':
            self.advance()
    @p.transition('q')
    def p(self):
        return self.symbol == 'q'
    @p.transition('final')
    def p(self):
        return self.symbol == ''

    @state('q')
    def q(self):
        while self.symbol == 'q':
            self.advance()
    @q.transition('final')
    def q(self):
        return self.symbol == ''

    @state('final')
    def final(self):
        raise Accept()

    def no_transition(self, s_name):
        raise Reject("Unexpected character")

    def on_reject(self, exc):
        self.error_msg = exc.args[0]


if __name__ == '__main__':
    from io import StringIO

    def report(fsm):
        accepted = fsm.run()
        if accepted:
            print('"{inp}" accepted.'.format(inp = fsm.stream.getvalue()))
        else:
            ptr = ' '*fsm.pos + '^'
            inp = fsm.stream.getvalue()
            msg = 'Rejected: {msg}\n{inp}\n{ptr}'.format(msg=fsm.error_msg,
                                                         inp=inp, ptr=ptr)
            print(msg)
        print('-'*60)

    print("NFA to accept the language (p^i)(q^j)")
    print('='*60)
    report(PsAndQs(StringIO("pppqqqqq")))
    report(PsAndQs(StringIO("qqqqpppp")))
    report(PsAndQs(StringIO("rppppqqqq")))
    report(PsAndQs(StringIO("pppprqqqq")))
    report(PsAndQs(StringIO("ppppqqqqr")))
    report(PsAndQs(StringIO("qqqqqqq")))
    report(PsAndQs(StringIO("pppppp")))

