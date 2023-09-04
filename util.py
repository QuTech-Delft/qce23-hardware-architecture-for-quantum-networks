from netsquid.qubits import qubitapi

from dataclasses import dataclass
from enum import Enum

from netsquid_physlayer.detectors import TwinDetector


def print_handler(message):
    """Bind to an output port to simply print and drop output messages."""
    print(message.items[0])


@dataclass
class Outcome:
    """Detector output. A and B denote the two detectors."""
    A: int
    B: int


class Detector(TwinDetector):
    """Simple detector with beam splitter as presented in the tutorial."""

    def __init__(self, p_dark=0., det_eff=1., num_resolving=True, visibility=1.):
        super().__init__(
            "Detector",
            p_dark=p_dark,
            det_eff=det_eff,
            visibility=visibility,
            num_resolving=num_resolving,
            num_input_ports=2,
            num_output_ports=2,
            meas_operators=[],
            output_meta={"successful_modes": [None]},
            dead_time=0.,
        )
        self._allow_multiple_successful_modes = False
        self._measoutcome2outcome = {0: Outcome(A=0, B=0),
                                     1: Outcome(A=1, B=0),
                                     2: Outcome(A=0, B=1),
                                     3: Outcome(A=1, B=1),
                                     4: Outcome(A=2, B=0),
                                     5: Outcome(A=0, B=2)}
        self.outcomes = []
        def outcome_handler(message):
            self.outcomes.append(message.items[0])
        self.ports["cout0"].bind_output_handler(outcome_handler)

    def preprocess_inputs(self):
        """Functionality incorporated in `measure()`"""
        pass

    def postprocess_outputs(self, dict_port_outcomes):
        """Functionality incorporated in `measure()`"""
        pass

    def measure(self):
        self._is_triggered = False
        if self._parameter_changed:
            self._set_meas_operators_with_beamsplitter()
            self._parameter_changed = False

        # Get all qubits per port.
        q_lists = [self._qubits_per_port[port_name] for port_name in self._input_port_names]
        arrival_times, qubits, __ = zip(*[item for q_list in q_lists for item in q_list])
        assert (len(qubits) // 2) == 1

        # Only perform a measurement if the two arrival times are exactly equal
        assert arrival_times[0] == arrival_times[1]

        # Perform pair-wise measurement for a single mode
        qubit_left, qubit_right = qubits[0], qubits[1]
        assert qubit_left.is_number_state
        assert qubit_right.is_number_state

        # Measure in presence-absence encoding
        outcome = qubitapi.gmeasure(
            [qubit_left, qubit_right], meas_operators=self._meas_operators)[0]
        outcome = self._measoutcome2outcome[outcome]

        # Append this outcome and the corresponding mode to be transmitted back in a classical
        # message and if multiple modes are not allowed break the for-loop so that the rest of
        # the qubits are not measured (iff not _allow_multiple_successful_modes)
        outcomes = [outcome]

        # Discard all the qubits
        [qubitapi.discard(qubit) for qubit in qubits if qubit is not None]
        self._qubits_per_port.clear()

        # Take the measurement outcomes and put the outcomes on the ports
        outcomes_per_port = {port_name: outcomes[:] for port_name in self._output_port_names}
        self.inform(outcomes_per_port)

        # Reset the meta information
        self.finish()


class BellState(Enum):
    PHI_P = "PHI_PLUS"
    PHI_M = "PHI_MINUS"
    PSI_P = "PSI_PLUS"
    PSI_M = "PSI_MINUS"


def get_state_after_swap(state_AB, swap_outcome, state_CD):
    """Combine input states with BSM outcome to get state after an entanglement swap."""
    outcome_bell_state = {
        (0, 0): BellState.PHI_P,
        (0, 1): BellState.PSI_P,
        (1, 0): BellState.PHI_M,
        (1, 1): BellState.PSI_M,
    }
    swap_state = outcome_bell_state[swap_outcome]

    state_sum = {
        BellState.PHI_P: {
            BellState.PHI_P: BellState.PHI_P,
            BellState.PHI_M: BellState.PHI_M,
            BellState.PSI_P: BellState.PSI_P,
            BellState.PSI_M: BellState.PSI_M,
        },
        BellState.PHI_M: {
            BellState.PHI_P: BellState.PHI_M,
            BellState.PHI_M: BellState.PHI_P,
            BellState.PSI_P: BellState.PSI_M,
            BellState.PSI_M: BellState.PSI_P,
        },
        BellState.PSI_P: {
            BellState.PHI_P: BellState.PSI_P,
            BellState.PHI_M: BellState.PSI_M,
            BellState.PSI_P: BellState.PHI_P,
            BellState.PSI_M: BellState.PHI_M,
        },
        BellState.PSI_M: {
            BellState.PHI_P: BellState.PSI_M,
            BellState.PHI_M: BellState.PSI_P,
            BellState.PSI_P: BellState.PHI_M,
            BellState.PSI_M: BellState.PHI_P,
        }
    }

    int_state = state_sum[state_AB][swap_state]
    final_state = state_sum[int_state][state_CD]

    return final_state
