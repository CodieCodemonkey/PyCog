"""State machine"""

from state import State, state

class Accept(Exception):
    """Accept the input stream."""
    pass

class Reject(Exception):
    """Reject the input stream."""
    pass

class MetaStateMachine(type):
    """Builds a tables of states and transitions."""

    def __new__(cls, name, bases, namespace, **kwd):
        state_map = dict()
        transition_map = dict()

        for name, entity in namespace.items():
            if type(entity) is State:
                state_map[entity.name] = entity
                continue
            transition = getattr(entity, '_transition', None)
            if transition != None:
                transition_map[transition] = entity

        namespace['_state_map'] = state_map

        result = type.__new__(cls, name, bases, namespace)
        return result

class StateMachine(metaclass=MetaStateMachine):
    def __init__(self, initial):
        self.state_name = initial
        self._initial = initial

    @property
    def state(self):
        """Get the current state object."""
        return self.get_state_from_name(self.state_name)

    # State forwards
    def enter(self):
        """Call the current state's on_enter handler."""
        method = self.state.on_enter
        return method(self)
    def exit(self):
        """Call the current state's on_exit handler."""
        method = self.state.on_exit
        return method(self)
    def no_transition(self):
        """Call the current state's no_transition handler."""
        method = self.state.no_transition
        return method(self)
    def while_active(self):
        """Call the current state's while_active handler."""
        method = self.state.while_active
        return method(self)

    def get_state_from_name(self, name):
        return self._state_map[name]

    def on_accept(self, exc):
        """
        Called when the input has been accepted.

        exc -- Exception triggering this event.
        """
        pass

    def on_reject(self, exc):
        """
        Called when the input has been rejected.

        exc -- Exception triggering this event.
        """
        pass

    def select_transition(self, qualifying_states):
        """
        Select a transition state from the list of qualifying states.

        qualifying_states -- List of qualifying states.

        returns the choice of state to receive the transition.
        """
        return qualifying_states[0]

    def on_transition(self, next_state):
        """
        Called when transitioning between states.

        next_state -- Entering state.
        """
        pass

    def run(self):
        """Run the state machine"""

        try:
            self.enter()
            while True:
                while self.while_active(): pass

                # Transitioning

                allowed_transitions = []
                for transition, next_state in self.state._transitions:
                    if transition(self):
                        allowed_transitions.append(next_state)

                self.exit()
                if len(allowed_transitions) == 0:
                    self.no_transition()
                    msg = "Cannot transition from state {st}"
                    raise Reject(msg.format(st = self.state_name))
                next_state = self.select_transition(allowed_transitions)
                self.on_transition(next_state)
                self.state_name = next_state
                self.enter()

        except Accept as exc:
            self.exit()
            self.on_accept(exc)
            return True
        except Reject as exc:
            self.exit()
            self.on_reject(exc)
            return False
        except:
            self.exit()
            raise

if __name__ == '__main__':

    class PsAndQs(StateMachine):
        def __init__(self, stream):
            super().__init__('p')

            print('='*60)
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

        @state('p')
        def p(self):
            chr = self.symbol
            if chr == 'p':
                self.advance()
                return True
            return False
        @p.transition('q')
        def p(self):
            return self.symbol == 'q'
        @p.transition('final')
        def p(self):
            return self.symbol == ''
        @p.no_transition
        def p(self):
            raise Reject("Unexpected character")
        @p.enter
        def p(self):
            print('Entering state "p"...')
        @p.exit
        def p(self):
            print('Exiting state "p"...')

        @state('q')
        def q(self):
            if self.symbol == 'q':
                self.advance()
                return True
            return False
        @q.transition('final')
        def q(self):
            return self.symbol == ''
        @q.no_transition
        def q(self):
            raise Reject("Unexpected character")
        @q.enter
        def q(self):
            print('Entering state "q"...')
        @q.exit
        def q(self):
            print('Exiting state "q"...')

        @state('final')
        def final(self):
            raise Accept()

        def on_transition(self, to_state):
            from_state = self.state.name
            print('Transitioning from "{f}" to "{t}"...'.format(f=from_state,
                                                                t=to_state))

        def on_reject(self, exc):
            ptr = ' '*self.pos + '^'
            inp = self.stream.getvalue()
            msg = 'Rejected: {msg}\n{inp}\n{ptr}'.format(msg=exc.args[0],
                                                         inp=inp, ptr=ptr)
            print(msg)

        def on_accept(self, exc):
            print('"{inp}" accepted.'.format(inp = self.stream.getvalue()))

    from io import StringIO

    print("NFA to accept the language (p^i)(q^j)")
    test = PsAndQs(StringIO("pppqqqqq"))
    test.run()
    test = PsAndQs(StringIO("qqqqpppp"))
    test.run()
    test = PsAndQs(StringIO("rppppqqqq"))
    test.run()
    test = PsAndQs(StringIO("pppprqqqq"))
    test.run()
    test = PsAndQs(StringIO("ppppqqqqr"))
    test.run()
    test = PsAndQs(StringIO("qqqqqqq"))
    test.run()
    test = PsAndQs(StringIO("pppppp"))
    test.run()

