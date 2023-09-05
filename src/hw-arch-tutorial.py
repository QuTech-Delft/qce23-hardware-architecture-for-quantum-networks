from netsquid.qubits import qubitapi, operators
import netsquid as ns

from netsquid_physlayer.pair_preparation import ExcitedPairPreparation

from util import BellState, Detector, get_state_after_swap


def detectors():
    detector = Detector(p_dark=0, det_eff=1, num_resolving=True, visibility=1.0)

    for _ in range(20):
        photons = qubitapi.create_qubits(2)

        photons[0].is_number_state = True
        photons[1].is_number_state = True

        # Step 1: Apply the X operator to both to put them in the |1> state.
        # TODO

        # Step 2: inject the two photons into the "qin0" and "qin1" port using
        # the ports' tx_input method.
        # TODO

        # This call will make NetSquid run for 1 nanosecond. This is sufficient
        # for us since we are not propagating along fiber.
        ns.sim_run(duration=1)

        # This will print the detector outcome.
        print(detector.outcomes.pop())


def heralding():
    # Under normal conditions the detectors are not number resolving. Howver, we will simulate
    # number resolving detectors for educational purposes.
    detector = Detector(p_dark=0, det_eff=1, num_resolving=True, visibility=1.0)

    failed = 0
    alpha = 0.3

    spin_photon_generator = ExcitedPairPreparation()

    TOTAL = 20
    for _ in range(TOTAL):
        # The alpha parameter is the bright state population.
        spin_left, photon_left = spin_photon_generator.generate(alpha)
        spin_right, photon_right = spin_photon_generator.generate(alpha)

        detector.ports["qin0"].tx_input(photon_left)
        detector.ports["qin1"].tx_input(photon_right)

        ns.sim_run(duration=1)

        outcome = detector.outcomes.pop()

        # Step 1: For each set ouf outcomes: are the two spins entangled? If so,
        # verify that they are in the expected Bell state.
        if (outcome.A == 2) or (outcome.B == 2):
            # TODO
            pass

        elif (outcome.A == 1):
            # TODO
            pass

        elif (outcome.B == 1):
            # TODO
            pass

        else:
            # TODO
            pass

    print(f"=== Succeeded {TOTAL-failed}/{TOTAL}")


def from_mp_outcome(mp_outcome):
    return (BellState.PSI_P if mp_outcome.A == 1 else
            BellState.PSI_M if mp_outcome.B == 1 else
            None)


def swapping():
    alpha = 0.2
    spin_photon_generator = ExcitedPairPreparation()

    link_AB = Detector(p_dark=0, det_eff=1, num_resolving=True, visibility=1.0)
    link_CD = Detector(p_dark=0, det_eff=1, num_resolving=True, visibility=1.0)

    failed = 0
    TOTAL = 10
    for _ in range(TOTAL):
        print("===")

        spin_A, spin_B, spin_C, spin_D = (None, ) * 4

        entangled_AB = None
        # Step 1: create entanglement between qubits A and B
        while entangled_AB is None:
            spin_A, photon_A = spin_photon_generator.generate(alpha)
            spin_B, photon_B = spin_photon_generator.generate(alpha)

            # TODO

        print(f"AB entangled :: {entangled_AB}")

        entangled_CD = None
        # Step 2: create entanglement between qubits C and D
        while entangled_CD is None:
            spin_C, photon_C = spin_photon_generator.generate(alpha)
            spin_D, photon_D = spin_photon_generator.generate(alpha)

            # TODO

        print(f"CD entangled :: {entangled_CD}")

        # Step 3: Perform the entanglement swap between qubits B and C and save the BSM outcome to
        # the `bsm` variable.
        # TODO

        print(f"Swap outcome :: {bsm}")

        # Get the state of AD after the entanglement swap.
        swapped_state = get_state_after_swap(entangled_AB, bsm, entangled_CD)

        print(f"Swapped state :: {swapped_state}")

        # Step 4: Apply the Pauli correction.
        if swapped_state == BellState.PHI_P:
            pass
        elif swapped_state == BellState.PHI_M:
            # TODO
            pass
        elif swapped_state == BellState.PSI_P:
            # TODO
            pass
        else:
            # TODO
            pass

        # Step 5: Verify the final AD state and save the final `BellState` value to the
        # `final_state` variable.
        # TODO

        print(f"Final state :: {final_state}")

        if final_state != BellState.PHI_P:
            failed += 1

    print(f"=== Succeeded {TOTAL-failed}/{TOTAL}")

if __name__ == "__main__":
    # Comment or to execute the desired exercise.
    detectors()
    heralding()
    swapping()
