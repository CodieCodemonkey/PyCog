import sys

if __name__ == '__main__':
    sys.path.append("../packages")

from pycog.statemachine import state
from pycog.pushdown import *
from pycog.trace import trace
from pycog.exceptions import Reject, Accept

# Symbols that we give special treatment to
container_symbols = '()[]{}'

# Transition test for states associated with container symbols.
# Args:
#     sm: state machine
#     s: the current active state
#     t: the target state of the transition
symbol_transition_test = lambda sm, s, t: sm.symbol == t

# transition test list used to transitions to container symbol states
symbol_transitions = [(s, symbol_transition_test) for s in container_symbols]

# Uncomment the next line to see a trace of the state machine.
# @trace
class ParenChecker(PushDown):

    def __init__(self, stream):
        super().__init__(initial='scan')

        self.stream = stream
        self._symbol = self.stream.read(1)
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

    def bad_match(self):
        self.error_msg = "'{st}' matched with '{en}' at position {pos}." 
        self.error_msg = self.error_msg.format(st=self.stack[-1],
                                               en=self.current_state,
                                               pos=self.pos)
        raise Reject()

    def unmatched(self):
        self.error_msg = "'{en}' unmatched at position {pos}." 
        self.error_msg = self.error_msg.format(en=self.current_state,
                                               pos=self.pos)
        raise Reject()

    @state('(')
    def open_paren(self):
        self.advance()
        self.push('scan')
    @open_paren.transition('scan')
    def open_paren(self): return True

    @state(')')
    def close_paren(self):
        self.advance()
        try:
            if self.stack[-1] != '(': self.bad_match()
        except IndexError:
            self.unmatched()
        self.pop()
    @close_paren.transition('scan')
    def close_paren(self): return True

    @state('[')
    def open_bracket(self):
        self.advance()
        self.push('scan')
    @open_bracket.transition('scan')
    def open_bracket(self): return True

    @state(']')
    def close_bracket(self):
        self.advance()
        try:
            if self.stack[-1] != '[': self.bad_match()
        except IndexError:
            self.unmatched()
        self.pop()
    @close_bracket.transition('scan')
    def close_bracket(self): return True

    @state('{')
    def open_brace(self):
        self.advance()
        self.push('scan')
    @open_brace.transition('scan')
    def open_brace(self): return True

    @state('}')
    def close_brace(self):
        self.advance()
        try:
            if self.stack[-1] != '{': self.bad_match()
        except IndexError:
            self.unmatched()
        self.pop()
    @close_brace.transition('scan')
    def close_brace(self): return True

    @state('scan', transitions=symbol_transitions)
    def scan(self):
        while self.symbol not in container_symbols:
            if self.symbol == '':
                if len(self.stack) != 0:
                    self.error_msg = "Unmatched symbol found"
                    raise Reject()
            self.advance()
    @scan.transition('final')
    def scan(self): return self.symbol == '' and len(self.stack) == 0

    def on_no_transition(self, s_name):
        self.error_msg = "No transition available--unknown cause."
        if len(self.stack) > 0:
            self.error_msg = "Symbol '{st}' not matched."
            self.error_msg = self.error_msg.format(st=self.stack[-1])

        super().on_no_transition(s_name)

    @state('final')
    def final(self):
        raise Accept()

if __name__ == '__main__':
    from io import StringIO

    def report(fsm):
        try:
            accepted = fsm.run()
            if accepted:
                print('"{inp}" accepted.'.format(inp = fsm.stream.getvalue()))
            else:
                ptr = ' '*fsm.pos + '^'
                inp = fsm.stream.getvalue()
                msg = 'Rejected: {msg}\n{inp}\n{ptr}'.format(msg=fsm.error_msg,
                                                             inp=inp, ptr=ptr)
                print(msg)
        finally:
            print('-'*60)

    print()
    print("PDA to accept strings with matching parens, braces, and brackets.")
    print('='*60)
    report(ParenChecker(StringIO("( )")))
    report(ParenChecker(StringIO("(")))
    report(ParenChecker(StringIO(")")))
    report(ParenChecker(StringIO("(([] {}) ())")))
    report(ParenChecker(StringIO("(([] {} ())")))
    report(ParenChecker(StringIO("(([] { ())")))
    report(ParenChecker(StringIO("(([] { () })")))

