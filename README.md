PyCog
=====

Python framework for automata of various sorts.

I'm just getting started, so bear with me.

Currently avoilable modules are:

<table>
  <tr>
    <th>Module</th><th>Description</th>
  </tr>
  <tr>
    <td>automata.statemachine</td>
    <td>Implements a state machine class.  Includes support for decorations for state activities and transitions.</td>
  </tr>
  <tr>
    <td>automata.backtrack</td>
    <td>Provides a mix-in class for easy backtracking over the state sequence.</td>
  </tr>
</table>

# Examples

Creating a NFA to read the language (p^i)(q^i) (0 or more 'p's followed by 0 or more 'q's) looks like this:

    class PsAndQs(StateMachine):
        def __init__(self, stream):
            StateMachine.__init__(self, 'init')

            self.stream = stream
            self.symbol = ''

        # Stream interface, eventually will be part of sequence NFAs.
        def advance(self):
            self.symbol = self.stream.read(1)
            return self.symbol

        def on_reject(self):
            print("Rejected!")
        def on_accept(self):
            print("Accepted!")

        @state('init')
        def init(self): pass
        @init.transition('p')
        def init.self): return self.symbol == 'p'
        @init.transition('q')
        def init.self): return self.symbol == 'q'
        @init.transition('final')
        def init(self): return self.symbol == ''

        @state('p')
        def p(self):
            while self.symbol == 'p': self.advance()
        @p.transition('q')
        def p.self): return self.symbol == 'q'
        @p.transition('final')
        def p(self): return self.symbol == ''

        @state('q')
        def q(self):
            while self.symbol == 'q': self.advance()
        @q.transition('final')
        def q(self): return self.symbol == ''

        @state('final')
        def final(self):
            raise Accept()

    from io import StringIO

Sample run:

<pre>
>>> test = PsAndQs(StringIO("pppqqqqq"))
>>> test.run()
Accepted!
>>> test = PsAndQs(StringIO("qqqqpppp"))
>>> test.run()
Rejected!
>>> test = PsAndQs(StringIO("rppppqqqq"))
>>> test.run()
Rejected!
>>> test = PsAndQs(StringIO("qqqqqqq"))
>>> test.run()
Accepted!
>>> test = PsAndQs(StringIO("pppppp"))
>>> test.run()
Accepted!
</pre>

