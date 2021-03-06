from functools import partial
from itertools import chain
from nac.common import retrieve_hdf5_data
from nac.workflows.workflow_coupling import generate_pyxaid_hamiltonians
from nac.workflows.workflow_AbsortionSpectrum import workflow_oscillator_strength
from nac.workflows.initialization import initialize
from nose.plugins.attrib import attr
from os.path import join
from qmworks.utils import dict2Setting

import h5py
import numpy as np
import os
import shutil


cp2k_main = dict2Setting({
    'cell_parameters': 28.0, 'potential': 'GTH-PBE',
    'basis': 'DZVP-MOLOPT-SR-GTH', 'specific':
    {'cp2k': {'force_eval':
              {'subsys': {'cell': {'periodic': 'None'}}, 'dft':
               {'print': {'mo': {'mo_index_range': '248 327'}},
                'scf': {'eps_scf': 0.0005, 'max_scf': 200,
                        'added_mos': 30}}}}},
    'cell_angles': [90.0, 90.0, 90.0]})

cp2k_guess = dict2Setting({
    'cell_parameters': 28.0, 'potential': 'GTH-PBE',
    'basis': 'DZVP-MOLOPT-SR-GTH', 'specific':
    {'cp2k': {'force_eval':
              {'subsys': {'cell': {'periodic': 'None'}},
               'dft': {'scf': {'eps_scf': 1e-06, 'ot':
                               {'minimizer': 'DIIS',
                                'n_diis': 7, 'preconditioner':
                                'FULL_SINGLE_INVERSE'},
                               'scf_guess': 'restart',
                               'added_mos': 0}}}}},
    'cell_angles': [90.0, 90.0, 90.0]})

# Environment data
basisname = 'DZVP-MOLOPT-SR-GTH'
path_traj_xyz = 'test/test_files/Cd33Se33_fivePoints.xyz'
scratch_path = 'scratch'
path_original_hdf5 = 'test/test_files/Cd33Se33.hdf5'
path_test_hdf5 = join(scratch_path, 'test.hdf5')
project_name = 'Cd33Se33'


@attr('slow')
def test_couplings_and_oscillators():
    """
    Test couplings and oscillator strength for Cd33Se33
    """
    if not os.path.exists(scratch_path):
        os.makedirs(scratch_path)
    try:
        shutil.copy('test/test_files/BASIS_MOLOPT', scratch_path)
        shutil.copy('test/test_files/GTH_POTENTIALS', scratch_path)

        # Run the actual test
        copy_basis_and_orbitals(path_original_hdf5, path_test_hdf5,
                                project_name)
        data = calculate_couplings_and_oscillators()
        # Check couplings
        check_properties()
        # Check oscillator
        fij = list(*chain(*data[0]))[5]
        assert abs(fij - 0.130748) < 1e-6

    finally:
        # remove tmp data and clean global config
        shutil.rmtree(scratch_path)


def calculate_couplings_and_oscillators():
    """
    Compute a couple of couplings with the Levine algorithm
    using precalculated MOs.
    """
    initial_config = initialize(
        project_name, path_traj_xyz,
        basisname=basisname, path_basis=None,
        path_potential=None, enumerate_from=0,
        calculate_guesses='first', path_hdf5=path_test_hdf5,
        scratch_path=scratch_path)

    generate_pyxaid_hamiltonians(
        'cp2k', project_name, cp2k_main,
        guess_args=cp2k_guess, nHOMO=50,
        couplings_range=(50, 30), **initial_config)

    data = workflow_oscillator_strength(
        'cp2k', project_name, cp2k_main, guess_args=cp2k_guess,
        nHOMO=50, couplings_range=(50, 30), initial_states=[50],
        energy_range=(0, 5),  # eV
        final_states=[[52]], **initial_config)

    return data


def check_properties():
    """
    Test if the coupling coupling by the Levine method is correct
    """
    # Paths to all the arrays to test
    path_swaps = join(project_name, 'swaps')
    name_Sji = 'overlaps_{}/mtx_sji_t0'
    name_Sji_fixed = 'overlaps_{}/mtx_sji_t0_corrected'
    path_overlaps = [join(project_name, name_Sji.format(i)) for i in range(4)]
    path_fixed_overlaps = [join(project_name, name_Sji_fixed.format(i))
                           for i in range(4)]
    path_couplings = [join(project_name, 'coupling_{}'.format(i))
                      for i in range(4)]

    # Define partial func
    fun_original = partial(stack_retrieve, path_original_hdf5)
    fun_test = partial(stack_retrieve, path_test_hdf5)

    # Read data from the HDF5
    swaps_original = retrieve_hdf5_data(path_original_hdf5, path_swaps)
    swaps_test = retrieve_hdf5_data(path_test_hdf5, path_swaps)

    overlaps_original = fun_original(path_overlaps)
    overlaps_test = fun_test(path_overlaps)

    fixed_overlaps_original = fun_original(path_fixed_overlaps)
    fixed_overlaps_test = fun_test(path_fixed_overlaps)

    css_original = fun_original(path_couplings)
    css_test = fun_test(path_couplings)

    # Test data
    b1 = np.allclose(swaps_original, swaps_test)
    b2 = np.allclose(overlaps_original, overlaps_test)
    b3 = np.allclose(fixed_overlaps_original, fixed_overlaps_test)
    b4 = np.allclose(css_original, css_test)

    assert all((b1, b2, b3, b4))


def stack_retrieve(path_hdf5, path_prop):
    """
    Retrieve a list of Numpy arrays and create a tensor out of it
    """
    return np.stack(retrieve_hdf5_data(path_hdf5, path_prop))


def copy_basis_and_orbitals(source, dest, project_name):
    """
    Copy the Orbitals and the basis set from one the HDF5 to another
    """
    keys = [project_name, 'cp2k']
    excluded = ['coupling', 'overlaps', 'swaps']
    with h5py.File(source, 'r') as f5, h5py.File(dest, 'w') as g5:
        for k in keys:
            if k not in g5:
                g5.create_group(k)
            for l in f5[k].keys():
                if not any(x in l for x in excluded):
                    path = join(k, l)
                    f5.copy(path, g5[k])
