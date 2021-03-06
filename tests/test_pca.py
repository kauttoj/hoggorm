'''
FIXME: PCA testing ideas:
 * Well known datasets (iris)
 * Combinations of input parameters
 * Edge case datasets
 * Big matrix for performance testing / profiling
 * Illegale data and error handling (zero variance)
 * Integer and float type matrix
'''
import os.path as osp

import numpy as np

import pytest

from hoggorm import nipalsPCA as PCA


# If the following equation is element-wise True, then allclose returns True.
# absolute(a - b) <= (atol + rtol * absolute(b))
# default: rtol=1e-05, atol=1e-08
rtol = 1e-05
atol = 1e-08


ATTRS = [
    'modelSettings',
    'X_means',
    'X_scores',
    'X_loadings',
    'X_corrLoadings',
    'X_residuals',
    'X_calExplVar',
    'X_cumCalExplVar_indVar',
    'X_cumCalExplVar',
    'X_predCal',
    'X_PRESSE_indVar',
    'X_PRESSE',
    'X_MSEE_indVar',
    'X_MSEE',
    'X_RMSEE_indVar',
    'X_RMSEE',
    'X_valExplVar',
    'X_cumValExplVar_indVar',
    'X_cumValExplVar',
    'X_predVal',
    'X_PRESSCV_indVar',
    'X_PRESSCV',
    'X_MSECV_indVar',
    'X_MSECV',
    'X_RMSECV_indVar',
    'X_RMSECV',
    #'X_scores_predict',
    'cvTrainAndTestData',
    'corrLoadingsEllipses'
]


def test_api_verify(pcacached, cfldat):
    """
    Check if all methods in list ATTR are also available in nipalsPCA class.
    """
    # First check those in list ATTR above. These don't have input parameters.
    for fn in ATTRS:
        res = getattr(pcacached, fn)()
        print(fn, type(res), '\n')
        if isinstance(res, np.ndarray):
            print(res.shape, '\n')
    
    # Now check those with input paramters
    res = pcacached.X_scores_predict(Xnew=cfldat)
    print('X_scores_predict', type(res), '\n')
    print(res.shape)


def test_constructor_api_variants(cfldat):
    print("\n")
    pca1 = PCA(cfldat)
    print("pca1")
    pca2 = PCA(cfldat, numComp=200, Xstand=False)
    print("pca2")
    pca3 = PCA(cfldat, Xstand=True, cvType=["loo"])
    print("pca3")
    pca4 = PCA(cfldat, numComp=2, cvType=["loo"])
    print("pca4")
    pca5 = PCA(cfldat, numComp=2, Xstand=False, cvType=["loo"])
    print("pca5")
    pca6 = PCA(cfldat, numComp=2, Xstand=False, cvType=["KFold", 3])
    print("pca6")
    pca7 = PCA(cfldat, numComp=2, Xstand=False, cvType=["lolo", [1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7]])
    print("pca7")


def test_compare_reference(pcaref, pcacached):
    rname, refdat = pcaref
    res = getattr(pcacached, rname)()
    if refdat is None:
        dump_res(rname, res)
        assert False, "Missing reference data for {}, data is dumped".format(rname)
    elif not np.allclose(res[:, :3], refdat[:, :3], rtol=rtol, atol=atol):
        dump_res(rname, res)
        assert False, "Difference in {}, data is dumped".format(rname)
    else:
        assert True


testMethods = ["X_scores", "X_loadings", "X_corrLoadings", "X_cumCalExplVar_indVar"]
@pytest.fixture(params=testMethods)
def pcaref(request, datafolder):
    rname = request.param
    refn = "ref_PCA_{}.tsv".format(rname.lower())
    try:
        refdat = np.loadtxt(osp.join(datafolder, refn))
    except FileNotFoundError:
        refdat = None

    return (rname, refdat)


@pytest.fixture(scope="module")
def pcacached(cfldat):
    return PCA(cfldat, cvType=["loo"])


@pytest.fixture(scope="module")
def cflnewdat(datafolder):
    '''Read fluorescence spectra on cheese samples and return as numpy array'''
    return np.loadtxt(osp.join(datafolder, 'data_cheese_fluo_newRand.tsv'), dtype=np.float64, skiprows=1)


def dump_res(rname, dat):
    dumpfolder = osp.realpath(osp.dirname(__file__))
    dumpfn = "dump_PCA_{}.tsv".format(rname.lower())
    np.savetxt(osp.join(dumpfolder, dumpfn), dat, fmt='%.9e', delimiter='\t')
