PyCog
=====

PyCog is a Python framework for abstract machines of various sorts.

Currently the only developer is me, Ken Hill ([codiecodemonkey.com/contact.html](codiecodemonkey.com/contact.html)).  I'm just getting started on PyCog, so bear with me.

These principles are be kept in mind in designing and extending PyCog:

1. Avoid reinvention, especially when quality solutions are already available.  Instead PyCog development will provide adaptors whenever possible so that other packages play well with PyCog and together.
2. Focus on the aesthetics of client's code.  It should be easy to write clear, elegant code using PyCog.
3. Separate algorithms from specific data structures where possible.  Instead, PyCog will focus on well-defined and documented "protocols" in the Pythonic sense.
4. Provide new solutions (instead of adapting existing ones) when necessitated by principles 1-3.


## License

PyCog is released under the *GNU LESSER GENERAL PUBLIC LICENSE version 3*.  See `LICENSE.md`.


## Modules

Currently available modules are:

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

## Examples

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

Sample run:

<pre>
>>> from io import StringIO
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

