PyCog
=====

PyCog is a Python framework for abstract machines of various sorts.

Currently the only developer is me, Ken Hill (my email name is the same as my GitHub name, at gmail.com).

These principles are be kept in mind in designing and extending PyCog:

1. Focus on the aesthetics of client's code.  It should be easy to write clear, elegant code using PyCog.
2. Avoid reinvention, especially when quality solutions are already available.  Instead PyCog development will provide adaptors whenever possible so that other packages play well with PyCog and together.

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
  <tr>
    <td>pushdown</td>
    <td>Implements a pushdown automata.</td>
  </tr>
  <tr>
    <td>graph</td>
    <td>Provides standard graph functionality, and adaptors so that PyCog can work with other graph implementations.</td>
  </tr>
</table>

Various utilities are also provided, notably the ability to generate state diagrams at runtime.

## Examples

Creating a NFA to read the language (p^i)(q^i) (0 or more 'p's followed by 0 or more 'q's) looks like this:

    class PsAndQs(InputTape, StateMachine):
        def __init__(self, stream):
            super().__init__(initial='i', stream=stream)

            self.error_msg = ''

        @state('i', transitions=['p', 'q'])
        def initial(self):
            pass

        @state('p', transitions=['p', 'q'], accepting=True)
        def p(self):
            self.advance()
        @p.guard
        def p(self):
            return self.symbol == 'p'

        @state('q', transitions=['q'], accepting=True)
        def q(self):
            self.advance()
        @q.guard
        def q(self):
            return self.symbol == 'q'

        def on_no_transition(self, s_name):
            if self.accept_test():
                raise Accept()
            raise Reject("Unexpected character")

        def on_reject(self, exc):
            super().on_reject(exc)

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

