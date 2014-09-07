"""Example DFA to read the language (p^n)(q^m)"""

if __name__ == "__main__":
    import sys
    import os.path as op
    sys.path.append(op.abspath(op.join('..', 'packages')))

from pycog.statemachine import *
from pycog.inputtape import *

class PsAndQs(InputTape, StateMachine):
    def __init__(self, stream):
        super().__init__(initial='i', stream=stream)

        self.error_msg = ''

    @state('i')
    def initial(self):
        pass
    @initial.transition('p')
    def p_test(self):
        return self.symbol == 'p'
    @initial.transition('q')
    def q_test(self):
        return self.symbol == 'q'

    @state('p', accepting=True)
    def p(self):
        self.advance()
    @p.transition('p')
    def p_test(self):
        return self.symbol == 'p'
    @p.transition('q')
    def q_test(self):
        return self.symbol == 'q'

    @state('q', accepting=True)
    def q(self):
        self.advance()
    @q.transition('q')
    def q_test(self):
        return self.symbol == 'q'

    def on_no_transition(self, s_name):
        if self.accept_test():
            raise Accept()
        raise Reject("Unexpected character")

    def on_reject(self, exc):
        super().on_reject(exc)

        self.error_msg = exc.args[0]

if __name__ == '__main__':
    from io import StringIO

    from pycog.utility.diagram import diagram

    with open("ps_and_qs.gv", "w") as gv_file:
        diagram(PsAndQs(StringIO("pppqqq")), gv_file)

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

