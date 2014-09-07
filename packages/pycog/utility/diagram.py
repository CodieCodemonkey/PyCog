"""Generate Graphvis diagrams."""

from pycog.exceptions import StateStackEmpty
import pycog.statemachine as sm

def diagram(fsm, stream):
    """
    Diagram a state machine in Graphviz format.
    """
    stream.write("digraph state\n{\n")
    stream.write('\trankdir="LR";\n')

    stream.write('\tstart [label="", shape="none"];\n')

    initial_state = None
    state_to_ord = dict()
    for ord, (state, record) in enumerate(fsm._state_records.items()):
        state_to_ord[state] = ord

        try:
            if record.state_dict['_initial']:
                initial_state = state
        except KeyError:
            pass

        stream.write("\ts" + str(ord) + ' [label="' + str(state) + '"')
        shape = 'circle'
        try:
            if record.state_dict['_accepting']:
                shape = 'doublecircle'
        except KeyError:
            pass

        stream.write(', shape="' + shape + '"')
        stream.write("];\n")

        try:
            if record.state_dict['_pop_state']:
                stream.write('\tpop' + str(ord) + ' [label="", shape="none"];\n')
        except KeyError:
            pass


    if initial_state:
        stream.write("\tstart->s" + str(state_to_ord[initial_state]) + ";")

    for state, record in fsm._state_records.items():
        for transition in record.transitions:
            try:
                label = record.transition_info[transition].label
                if label == None:
                    label = ""
            except:
                label = ""

            stream.write("\ts" + str(state_to_ord[state]) + '->')
            stream.write("s" + str(state_to_ord[transition]))
            try:
                if record.state_dict['_push_state']:
                    stream.write(' [label="' + label +\
                                 '", arrowhead="normalnormal"]')
            except KeyError:
                stream.write(' [label="' + label + '"]')

            stream.write(';\n')

        try:
            if record.state_dict['_pop_state']:
                ord = state_to_ord[state]
                stream.write("\ts" + str(ord) + '->')
                stream.write("pop" + str(ord))
                stream.write(';\n')
        except KeyError:
            pass

    stream.write("}\n")

