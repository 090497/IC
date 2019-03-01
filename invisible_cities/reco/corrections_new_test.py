import os
import numpy  as np
from . corrections_new import maps_coefficient_getter
from . corrections_new import read_maps
from . corrections_new import e0_xy_corrections
from . corrections_new import lt_xy_corrections
from . corrections_new import ASectorMap
from . corrections_new import FitMapValue
from pytest                import fixture, mark
from numpy.testing         import assert_allclose
from hypothesis.strategies import floats
from hypothesis.strategies import integers
from hypothesis.strategies import composite
from hypothesis.strategies import lists
from hypothesis            import given


@fixture(scope='session')
def map_filename(ICDATADIR):
    test_file = "kr_emap_xy_constant_values.h5"
    test_file = os.path.join(ICDATADIR, test_file)
    return test_file

@fixture(scope='session')
def map_filename_MC(ICDATADIR):
    test_file = "kr_emap_xy_constant_values_RN_negat.h5"
    test_file = os.path.join(ICDATADIR, test_file)
    return test_file

@fixture
def toy_corrections():
    xs,ys = np.meshgrid(np.linspace(-199,199,5),np.linspace(-199,199,5))
    xs=xs.flatten(); ys=ys.flatten()
    zs = np.ones(25)
    es = np.ones(25)
    e0_corrections = np.array([9.43322064e-05, 9.43322064e-05, 9.43322064e-05, 9.43322064e-05,
                               9.43322064e-05, 9.43322064e-05, 8.39198694e-05, 8.32223502e-05,
                               9.13077163e-05, 9.43322064e-05, 9.43322064e-05, 8.32826455e-05,
                               8.02149510e-05, 8.70309002e-05, 9.43322064e-05, 9.43322064e-05,
                               9.20405803e-05, 8.84955546e-05, 9.56684281e-05, 9.43322064e-05,
                               9.43322064e-05, 9.43322064e-05, 9.43322064e-05, 9.43322064e-05,
                               9.43322064e-05])
    lt_corrections = np.array([1.0002771 , 1.0002771 , 1.0002771 , 1.0002771 , 1.0002771 ,
                               1.0002771 , 1.00023523, 1.0002237 , 1.00026303, 1.0002771 ,
                               1.0002771 , 1.00024245, 1.00027317, 1.00027545, 1.0002771 ,
                               1.0002771 , 1.00029724, 1.00029364, 1.0002934 , 1.0002771 ,
                               1.0002771 , 1.0002771 , 1.0002771 , 1.0002771 , 1.0002771 ])
    xy_geo_matrix  = np.array([10600.83335512, 10600.83335512, 10600.83335512, 10600.83335512,
                               10600.83335512, 10600.83335512, 11916.12912023, 12016.00288243,
                               10951.97690475, 10600.83335512, 10600.83335512, 12007.30349264,
                               12466.50390868, 11490.17185802, 10600.83335512, 10600.83335512,
                               10864.77287088, 11300.00262915, 10452.76921306, 10600.83335512,
                               10600.83335512, 10600.83335512, 10600.83335512, 10600.83335512,
                               10600.83335512])
    xy_lt_matrix   = np.array([3609.30708684, 3609.30708684, 3609.30708684, 3609.30708684,
                               3609.30708684, 3609.30708684, 4251.67968216, 4470.78086144,
                               3802.38482442, 3609.30708684, 3609.30708684, 4124.99577806,
                               3661.21394636, 3630.89659737, 3609.30708684, 3609.30708684,
                               3364.7524234 , 3405.97343322, 3408.77553025, 3609.30708684,
                               3609.30708684, 3609.30708684, 3609.30708684, 3609.30708684,
                               3609.30708684])
    return xs, ys, zs, es, e0_corrections, lt_corrections,xy_geo_matrix, xy_lt_matrix

def test_maps_coefficient_getter_exact(toy_corrections, correction_map_filename):
    maps=read_maps(correction_map_filename)
    xs, ys, zs, es, _, _, coef_geo, coef_lt = toy_corrections
    get_maps_coefficient_e0= maps_coefficient_getter(maps.mapinfo, maps.e0)
    CE  = get_maps_coefficient_e0(xs,ys)
    get_maps_coefficient_lt= maps_coefficient_getter(maps.mapinfo, maps.lt)
    LT  = get_maps_coefficient_lt(xs,ys)
    assert_allclose (CE, coef_geo)
    assert_allclose (LT, coef_lt)

@mark.skip
def test_e0_xy_corrections_exact(toy_corrections, correction_map_filename):
    maps=read_maps(correction_map_filename)
    xs, ys, zs, es, e0_correct, lt_correct, _, _ = toy_corrections
    e0_correct_test = e0_xy_corrections(es, xs, ys, maps)
    lt_correct_test = lt_xy_corrections(es, xs, ys, zs, maps)
    assert_allclose (e0_correct_test, e0_correct)
    assert_allclose (lt_correct_test, lt_correct)

def test_read_maps_returns_ASectorMap(correction_map_filename):
    maps=read_maps(correction_map_filename)
    assert type(maps)==ASectorMap


@composite
def xy_pos(draw, elements=floats(min_value=-250, max_value=250)):
    size = draw(integers(min_value=1, max_value=10))
    x    = draw(lists(elements,min_size=size, max_size=size))
    y    = draw(lists(elements,min_size=size, max_size=size))
    return (np.array(x),np.array(y))

@given(xy_pos = xy_pos())
def test_maps_coefficient_getter_gives_nans(correction_map_filename, xy_pos):
    x,y=xy_pos
    maps=read_maps(correction_map_filename)
    mapinfo = maps.mapinfo
    map_df  = maps.e0
    xmin,xmax = mapinfo.xmin,mapinfo.xmax
    ymin,ymax = mapinfo.ymin,mapinfo.ymax
    get_maps_coefficient_e0= maps_coefficient_getter(mapinfo, map_df)
    CE  = get_maps_coefficient_e0(x,y)
    mask_x   = (x >=xmax) | (x<xmin)
    mask_y   = (y >=ymax) | (y<ymin)
    mask_nan = (mask_x)   | (mask_y)
    assert all(np.isnan(CE[mask_nan]))
    assert not any(np.isnan(CE[~mask_nan]))

def test_amap_max_returns_FitMapValue(map_filename):
    maps       = read_maps(map_filename)
    max_values = amap_max(maps)
    assert type(max_values)==FitMapValue

def test_read_maps_when_MC_t_evol_is_none(map_filename_MC):
    emap = read_maps(map_filename_MC)
    assert emap.t_evol is None

def test_read_maps_t_evol_table_is_correct(map_filename):
    """
    For this test, a map where its t_evol table correspond to single values
    (ts=[1,1,...1], e0=[2,2,...2], ..., Yrmsu=[27,27,...27])
    has been generated.
    """

    maps       = read_maps(map_filename)
    map_te     = maps.t_evol
    columns_te = map_te.columns
    assert np.all([np.all( map_te[parameter] == i+1 )
                   for i, parameter in zip( range(len(columns_te)), columns_te )])


def test_read_maps_maps_are_correct(map_filename):
    """
    For this test, a map where its correction maps are:
    (chi=[1,1,...1], e0=[13000,13000,...13000], e0u=[2,2,...2],
    lt=[5000,5000,...5000], ltu=[3,3,...3])
    has been generated.
    """

    maps = read_maps(map_filename)
    assert np.all(maps.chi2 == 1    )
    assert np.all(maps.e0   == 13000)
    assert np.all(maps.e0u  == 2    )
    assert np.all(maps.lt   == 5000 )
    assert np.all(maps.ltu  == 3    )
