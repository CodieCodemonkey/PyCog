PyCog
=====

PyCog is a Python framework for abstract machines of various sorts.

Currently the only developer is me, Ken Hill (codiecodemonkey.com/contact.html).  I'm just getting started on PyCog, so bear with me.

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
    <td>statemachine</td>
    <td>Implements a state machine class.  Includes support for decorations for state activities and transitions.</td>
  </tr>
  <tr>
    <td>backtrack</td>
    <td>Provides a mix-in class for easy backtracking over the state sequence.</td>
  </tr>
</table>

## Examples

Creating a NFA to read the language (p^i)(q^i) (0 or more 'p's followed by 0 or more 'q's) looks like this:

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


Sample run:

<pre>
>>> from io import StringIO
>>> test = PsAndQs(StringIO("pppqqqqq"))
>>> test.run()
True
>>> test = PsAndQs(StringIO("qqqqpppp"))
>>> test.run()
False
>>> test = PsAndQs(StringIO("rppppqqqq"))
>>> test.run()
False
>>> test = PsAndQs(StringIO("qqqqqqq"))
>>> test.run()
True
>>> test = PsAndQs(StringIO("pppppp"))
>>> test.run()
True
</pre>

