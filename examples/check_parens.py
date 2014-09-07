import sys

if __name__ == '__main__':
    sys.path.append("../packages")

from pycog.statemachine import state, transition_always
from pycog.pushdown import *
from pycog.inputtape import *
from pycog.utility.trace import trace
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
class ParenChecker(InputTape, PushDown):

    def __init__(self, stream):
        super().__init__(initial='scan', stream=stream)

        # Record the symbol position in the stack frame for better error
        # reporting.
        self.active_frame.pos = 0

        self.error_msg = ''

        self.pos = 0

        self.open_symbol_pos = None
        self.close_symbol_pos = None

    def on_init_frame(self, frame):
        super().on_init_frame(frame)

        # Track the position of pushes and pops in the stack frame.
        frame.pos = -1
    def on_suspend_state(self, s_name):
        super().on_suspend_state(s_name)

        # Update the stack frame when suspending (before the frame is pushed)
        # so that we can use the position for error processing.  In our case
        # the position is the location of an open symbol.
        self.active_frame.pos = self.pos

    @property
    def symbol(self):
        """Return the current symbol"""
        return self._symbol

    def advance(self):
        """Advance the stream position"""
        self._symbol = self.stream.read(1)
        self.pos += 1
        return self._symbol

    def unmatched_open(self):
        self.open_symbol_pos = self.top_frame.pos - 1

        self.error_msg = "'{en}' unmatched at position {pos}." 
        self.error_msg = self.error_msg.format(en=self.top_frame.state,
                                               pos=self.open_symbol_pos)
        raise Reject()

    def unmatched_close(self):
        self.close_symbol_pos = self.pos - 1

        self.error_msg = "'{en}' unmatched at position {pos}." 
        self.error_msg = self.error_msg.format(en=self.current_state,
                                               pos=self.close_symbol_pos)
        raise Reject()

    def bad_match(self):
        self.open_symbol_pos = self.top_frame.pos - 1
        self.close_symbol_pos = self.pos - 1

        self.error_msg = "'{st}' at position {pos1} matched with '{en}' at "\
                "position {pos2}." 
        self.error_msg = self.error_msg.format(st=self.top_frame.state,
                                               pos1=self.open_symbol_pos,
                                               en=self.current_state,
                                               pos2=self.close_symbol_pos)
        raise Reject()

    @push_state('(', resume='scan', transitions=[('scan', transition_always)])
    def open_paren(self):
        # Record the open sympol position in the stack frame for error
        # reporting
        self.advance()

    @pop_state(')')
    def close_paren(self):
        self.advance()
        if self.stack_empty: 
            self.unmatched_close()
        if self.top_frame.state != '(':
            self.bad_match()

    @push_state('[', resume='scan', transitions=[('scan', transition_always)])
    def open_bracket(self):
        self.advance()

    @pop_state(']')
    def close_bracket(self):
        self.advance()
        if self.stack_empty: 
            self.unmatched_close()
        if self.top_frame.state != '[':
            self.bad_match()

    @push_state('{', resume='scan', transitions=[('scan', transition_always)])
    def open_brace(self):
        self.advance()

    @pop_state('}')
    def close_brace(self):
        self.advance()
        if self.stack_empty: 
            self.unmatched_close()
        if self.top_frame.state != '{':
            self.bad_match()

    @state('scan', transitions=symbol_transitions)
    def scan(self):
        while self.symbol and self.symbol not in container_symbols:
            self.advance()

    def on_no_transition(self, s_name):
        if self.accept_test():
            raise Accept()

        self.error_msg = "No transition available--unknown cause."
        if not self.stack_empty:
            self.unmatched_open()

        super().on_no_transition(s_name)

if __name__ == '__main__':
    from io import StringIO

    from pycog.utility.diagram import diagram
    with open("check_parens.gv", "w") as gv_file:
        diagram(ParenChecker(StringIO("()")), gv_file)

    def report(fsm):
        try:
            accepted = fsm.run()
            if accepted:
                print('"{inp}" accepted.'.format(inp = fsm.stream.getvalue()))
            else:
                inp = fsm.stream.getvalue()
                ptr = ""
                if fsm.open_symbol_pos != None:
                    ptr = ' '*fsm.open_symbol_pos + '^'
                    if fsm.close_symbol_pos != None:
                        ptr += ' '*(fsm.close_symbol_pos - fsm.open_symbol_pos
                                   - 1) + '^'
                elif fsm.close_symbol_pos != None:
                    ptr = ' '*fsm.close_symbol_pos + '^'


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

