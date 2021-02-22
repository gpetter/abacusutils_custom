import tempfile
import filecmp
import os.path
import numbers

import pytest
from astropy.table import Table
import numpy as np

EXAMPLE_SIM = os.path.join(os.path.dirname(__file__), 'Mini_N64_L32')
HALOS_OUTPUT_UNCLEAN = os.path.join(os.path.dirname(__file__), 'test_halos_unclean.asdf')
PARTICLES_OUTPUT_UNCLEAN = os.path.join(os.path.dirname(__file__), 'test_subsamples_unclean.asdf')
HALOS_OUTPUT_CLEAN = os.path.join(os.path.dirname(__file__), 'test_halos_clean.asdf')
PARTICLES_OUTPUT_CLEAN = os.path.join(os.path.dirname(__file__), 'test_subsamples_clean.asdf')

def test_halos_unclean(tmp_path):
    '''Test loading a base (uncleaned) halo catalog
    '''

    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, fields='all', cleaned_halos=False)

    # to regenerate reference
    #ref = cat.halos
    #import asdf; asdf.compression.set_compression_options(typesize='auto')
    #ref.write(HALOS_OUTPUT_UNCLEAN, all_array_storage='internal', all_array_compression='blsc')

    ref = Table.read(HALOS_OUTPUT_UNCLEAN)

    halos = cat.halos
    for col in ref.colnames:
        if issubclass(ref[col].dtype.type, numbers.Integral):
            assert np.all(halos[col] == ref[col])
        else:
            assert np.allclose(halos[col], ref[col])

    assert halos.meta == ref.meta

def test_halos_clean(tmp_path):
    '''Test loading a base (uncleaned) halo catalog
    '''

    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, fields='all', cleaned_halos=True)

    # to regenerate reference
    #ref = cat.halos
    #import asdf; asdf.compression.set_compression_options(typesize='auto')
    #ref.write(HALOS_OUTPUT_CLEAN, all_array_storage='internal', all_array_compression='blsc')

    ref = Table.read(HALOS_OUTPUT_CLEAN)

    halos = cat.halos
    for col in ref.colnames:
        if issubclass(ref[col].dtype.type, numbers.Integral):
            assert np.all(halos[col] == ref[col])
        else:
            assert np.allclose(halos[col], ref[col])

    # all haloindex values should point to this slab
    assert np.all((halos['haloindex']/1e12).astype(int) == cat.header['FullStepNumber'])
    # ensure that all deleted halos in ref are marked as merged in EXAMPLE_SIM
    assert np.all(halos['is_merged_to'][ref['N']==0] != -1)
    # no deleted halos in ref should have merged particles in EXAMPLE_SIM
    assert np.all(halos['N_merge'][ref['N']==0] == 0)

    assert halos.meta == ref.meta

def test_subsamples_unclean(tmp_path):
    '''Test loading particle subsamples
    '''

    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, fields='all', cleaned_halos=False)

    # to regenerate reference
    #ref = cat.subsamples
    #import asdf; asdf.compression.set_compression_options(typesize='auto')
    #ref.write(PARTICLES_OUTPUT_UNCLEAN, format='asdf', all_array_storage='internal', all_array_compression='blsc')

    ref = Table.read(PARTICLES_OUTPUT_UNCLEAN)

    ss = cat.subsamples
    for col in ref.colnames:
        if issubclass(ref[col].dtype.type, numbers.Integral):
            assert np.all(ss[col] == ref[col])
        else:
            assert np.allclose(ss[col], ref[col])

    assert cat.subsamples.meta == ref.meta

def test_subsamples_clean(tmp_path):
    '''Test loading particle subsamples
    '''

    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, fields='all', cleaned_halos=True)

    # to regenerate reference
    #ref = cat.subsamples
    #import asdf; asdf.compression.set_compression_options(typesize='auto')
    #ref.write(PARTICLES_OUTPUT_CLEAN, format='asdf', all_array_storage='internal', all_array_compression='blsc')

    ref = Table.read(PARTICLES_OUTPUT_CLEAN)

    ss = cat.subsamples
    for col in ref.colnames:
        if issubclass(ref[col].dtype.type, numbers.Integral):
            assert np.all(ss[col] == ref[col])
        else:
            assert np.allclose(ss[col], ref[col])

    # total number of particles in ref should be equal to the sum total of npout{AB} in EXAMPLE_SIM
    assert len(ref) == np.sum(cat.halos['npoutA']) + np.sum(cat.halos['npoutB'])

    assert cat.subsamples.meta == ref.meta

def test_field_subset_loading():
    '''Test loading a subset of halo catalog columns
    '''
    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), fields=['N','x_com'])
    assert set(cat.halos.colnames) == set(['N','x_com'])


def test_one_halo_info():
    '''Test loading a single halo_info file
    '''
    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000', 'halo_info', 'halo_info_000.asdf'),
        subsamples=True)
    assert len(cat.halos) == 127
    assert len(cat.subsamples) == 3209 #9306


def test_halo_info_list():
    '''Test list of halo infos
    '''
    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog

    cat = CompaSOHaloCatalog(
        [os.path.join(EXAMPLE_SIM, 'halos', 'z0.000', 'halo_info', 'halo_info_000.asdf'),
         os.path.join(EXAMPLE_SIM, 'halos', 'z0.000', 'halo_info', 'halo_info_001.asdf')],
        subsamples=True)
    assert len(cat.halos) == 281
    assert len(cat.subsamples) == 6900 #19555

    # check fail on dups
    with pytest.raises(ValueError):
        cat = CompaSOHaloCatalog(
        [os.path.join(EXAMPLE_SIM, 'halos', 'z0.000', 'halo_info', 'halo_info_000.asdf'),
         os.path.join(EXAMPLE_SIM, 'halos', 'z0.000', 'halo_info', 'halo_info_000.asdf')])


def test_unpack_bits():
    '''Test unpack_bits
    '''

    from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog
    from abacusnbody.data.bitpacked import PID_FIELDS

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, unpack_bits=True, fields='N')
    assert set(PID_FIELDS) <= set(cat.subsamples.colnames)  # check subset

    cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, unpack_bits='density', fields='N')
    assert 'density' in cat.subsamples.colnames
    assert 'lagr_pos' not in cat.subsamples.colnames  # too many?

    # bad bits field name
    with pytest.raises(ValueError):
        cat = CompaSOHaloCatalog(os.path.join(EXAMPLE_SIM, 'halos', 'z0.000'), subsamples=True, unpack_bits=['blah'], fields='N')
