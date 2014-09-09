import sys
import string
import unicodedata as ud

if __name__ == '__main__':
    sys.path.append("../packages")

from pycog.statemachine import state
from pycog.pushdown import *
from pycog.utility.trace import trace
from pycog.utility.treedump import treedump
from pycog.exceptions import Reject, Accept, StateStackEmpty
from pycog.graph import Graph, is_tree


def is_whitespace(chr):
    """True if chr is whitespace"""
    if chr in string.whitespace:
        return True
    return ud.category(chr) in ['Zs', 'Cc']

def is_id_start(chr):
    if chr == '_':
        return True
    return ud.category(chr) in ['LC', 'Ll', 'Lm', 'Lo', 'Lt', 'Lu']

def is_id_continuation(chr):
    if chr == '_':
        return True
    return ud.category(chr) in ['LC', 'Ll', 'Lm', 'Lo', 'Lt', 'Lu', 'Nd']

# Symbols that we give special treatment to
punctuation = '(),'

# Transition test for states associated with punctuation
punct_transition_test = lambda sm, s, t: sm.symbol == t

# transition test list for punctuation states
punctuation_transitions = [(s, punct_transition_test) for s in punctuation]

def ws_transition_test(sm, s, t):
    """transition test for whitespace"""
    if sm.symbol == '':
        return False
    return is_whitespace(sm.symbol)

def id_transition_test(sm, s, t):
    """transition test for identifiers"""
    if sm.symbol == '':
        return False
    return is_id_start(sm.symbol)

class SimpleExprNode:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return '<SimpleExprNode({v})>'.format(v=self.value)

# Uncomment the next line to see a trace of the state machine.
#@trace
class ParseSimpleExpr(PushDown):
    """
    Create a tree from an expression.

    An expression for our purposes is given by:
        id ::= ("_" | LETTER) ("_" | LETTER | DIGIT)*
        expr ::= id [ "(" [ expr ("," expr)* ] ")" ]
        (Whitespace is allowed anywhere except in an id)

        "a( b2, c (_, d))" is a valid expression.
    """

    def __init__(self, stream, graph):
        super().__init__(initial='scan')

        self.stream = stream
        self._symbol = self.stream.read(1)

        # Record the symbol position in the stack frame for better error
        # reporting.
        self.active_frame.pos = 0

        self.error_msg = ''

        self.pos = 0

        self.open_symbol_pos = None
        self.close_symbol_pos = None

        self.tree = graph
        self.cur_node = ""

    def on_init_frame(self, frame):
        super().on_init_frame(frame)

        # Track the position of pushes and pops in the stack frame.
        frame.pos = -1

        frame.node = ""

    def on_suspend_state(self, s_name):
        super().on_suspend_state(s_name)

        self.active_frame.pos = self.pos
        self.active_frame.node = self.node

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

    @push_state('(', resume='scan', transitions=['scan'])
    def open_paren(self):
        # Record the open symbol position in the stack frame for error
        # reporting
        self.advance()

    @pop_state(')')
    def close_paren(self):
        self.advance()
        if self.stack_empty: 
            self.unmatched_close()
        if self.top_frame.state != '(':
            self.bad_match()

    @state(',', transitions = ['scan'])
    def comma(self):
        self.advance()

    @state('id', transitions=['scan'])
    def id(self):
        id_chars = []
        while self.symbol and is_id_continuation(self.symbol):
            id_chars.append(self.symbol)
            self.advance()
        self.node = SimpleExprNode(''.join(id_chars))
        self.tree.add(self.node)
        if not self.stack_empty:
            self.tree.connect(self.top_frame.node, self.node)

    @state('ws', transitions=['scan'])
    def ws(self):
        while self.symbol and is_whitespace(self.symbol):
            self.advance()

    @state('scan', transitions=punctuation_transitions  + 
           [('ws', ws_transition_test), ('id', id_transition_test)])
    def scan(self):
        pass
    @scan.transition('final')
    def scan(self): return self.symbol == '' and self.stack_empty

    def on_no_transition(self, s_name):
        self.error_msg = "No transition available--unknown cause."
        if not self.stack_empty:
            self.unmatched_open()

        super().on_no_transition(s_name)

    @state('final')
    def final(self):
        raise Accept()

if __name__ == '__main__':
    from io import StringIO

    expr1 = """
        animals ( 
            canines ( domestic(dogs), 
                wild ( wolves, coyotes ) ),
            felines ( domestic(house_cats), 
                wild ( lions, tigers, cheetahs, leopards )))
    """

    tree = Graph()
    parser = ParseSimpleExpr(StringIO(expr1), tree)
    parser.run()

    print("\nExpression:", expr1)
    print("\nExpression tree:\n")
    treedump(tree)

