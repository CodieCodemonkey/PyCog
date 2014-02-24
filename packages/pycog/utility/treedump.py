"""Implementation of TreeDump"""

from pycog.statemachine import state, transition_always
from pycog.pushdown import PushDown, push_state, pop_state
from pycog.graph import GraphWrapper, is_tree
from pycog.exceptions import StateStackEmpty

class TreeDumper(PushDown):
    """
    Utility class to display a tree structure to sys.stdout
    """

    def __init__(self, tree, **kw_args):
        super().__init__(initial='write', **kw_args)

        if type(tree) is GraphWrapper:
            self.tree = tree
        else:
            self.tree = GraphWrapper(tree)

        self.root = is_tree(self.tree)
        if self.root == None:
            raise TypeError("Graph is not a tree.")

        self.indent = 0

        self.active_frame.node = self.root
        self.active_frame.children = []

    def on_suspend_state(self, s_name):
        self.indent += 1
        super().on_suspend_state(s_name)

    def on_resume_state(self, s_name):
        self.indent -= 1
        super().on_resume_state(s_name)

    @state("write", transitions=[('children', transition_always)])
    def write(self):
        indent_str = ""
        for frame in self.stack:
            if frame.children:
                if frame == self.top_frame:
                    indent_str += "|--"
                else:
                    indent_str += "|  "
            else:
                if frame == self.top_frame:
                    indent_str += "`--"
                else:
                    indent_str += "   "

        print(indent_str + str(self.active_frame.node))

    @state('next')
    def next(self):
        try:
            self.active_frame.node = self.top_frame.children.pop(0)
        except IndexError:
            self.active_frame.node = None
        except StateStackEmpty:
            self.active_frame.node = None
    @next.transition('write')
    def transition_write(self):
        return self.active_frame.node != None
    @next.transition('final')
    def transition_final(self):
        return self.stack_empty
    @next.transition('pop')
    def transition_pop(self):
        return True

    @push_state("children", resume='next',
                transitions=[('next', transition_always)])
    def children(self):
        parent = self.active_frame.node
        self.active_frame.children = [x for x in self.tree.succ(parent)]

    @pop_state("pop")
    def pop(self):
        pass

    @state('final')
    def final(self):
        pass

def treedump(tree):
    """
    Dump a tree to stdout.
    """
    dumper = TreeDumper(tree)
    dumper.run()

