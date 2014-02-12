"""Support for debug tracing"""

def trace(cls):
    """
    Trace decorator for automata.

    Generates a trace of the various states as they are encountered.

    Args:
        cls: Class object to modify.
    """

    indent_str = '|   '

    old_init = cls.__init__
    def __init__(self, *args, **kw_args):
        nonlocal old_init
        self._trace_indent = 0
        return old_init(self, *args, **kw_args)
    cls.__init__ = __init__

    if hasattr(cls, 'on_enter_state'):
        old_on_enter_state = cls.on_enter_state
        def on_enter_state(self, s_name):
            nonlocal indent_str, old_on_enter_state
            print(indent_str*self._trace_indent + "enter '" + str(s_name) + "'")
            return old_on_enter_state(self, s_name)
        cls.on_enter_state = on_enter_state

    if hasattr(cls, 'on_exit_state'):
        old_on_exit_state = cls.on_exit_state
        def on_exit_state(self, s_name):
            nonlocal indent_str, old_on_exit_state
            print(indent_str*self._trace_indent + "exit '" + str(s_name) + "'")
            return old_on_exit_state(self, s_name)
        cls.on_exit_state = on_exit_state

    if hasattr(cls, 'on_suspend_state'):
        old_on_suspend_state = cls.on_suspend_state
        def on_suspend_state(self, s_name):
            nonlocal indent_str, old_on_suspend_state
            print(indent_str*self._trace_indent + "suspend '" + str(s_name) + "'")
            self._trace_indent += 1
            return old_on_suspend_state(self, s_name)
        cls.on_suspend_state = on_suspend_state

    if hasattr(cls, 'on_resume_state'):
        old_on_resume_state = cls.on_resume_state
        def on_resume_state(self, s_name):
            nonlocal indent_str, old_on_resume_state
            self._trace_indent -= 1
            print(indent_str*self._trace_indent + "resume '" + str(s_name) + "'")
            return old_on_resume_state(self, s_name)
        cls.on_resume_state = on_resume_state

    if hasattr(cls, 'on_accept'):
        old_on_accept = cls.on_accept
        def on_accept(self, s_name):
            nonlocal indent_str, old_on_accept
            print(indent_str*self._trace_indent + "*** accepted.")
            return old_on_accept(self, s_name)
        cls.on_accept = on_accept

    if hasattr(cls, 'on_reject'):
        old_on_reject = cls.on_reject
        def on_reject(self, s_name):
            nonlocal indent_str, old_on_reject
            print(indent_str*self._trace_indent + "*** rejected.")
            return old_on_reject(self, s_name)
        cls.on_reject = on_reject

    return cls

