import os
import pytest
import pandas as pd
import numpy as np

from dgpost.transform import catalysis
from dgpost.utils import transform
from .utils import compare_dfs


@pytest.mark.parametrize(
    "inpath, spec, outpath",
    [
        (  # ts0 - dataframe with floats
            "xinxout.float.df.pkl",
            [
                {"feedstock": "C3H8", "xin": "xin", "xout": "xout"},
            ],
            "Yp.float.pkl",
        ),
        (  # ts1 - dataframe with ufloats
            "xinxout.ufloat.df.pkl",
            [
                {"feedstock": "propane", "element": "C", "xin": "xin", "xout": "xout"},
            ],
            "Yp.ufloat.pkl",
        ),
    ],
)
def test_yield_against_df(inpath, spec, outpath, datadir):
    os.chdir(datadir)
    df = pd.read_pickle(inpath)
    for args in spec:
        catalysis.catalytic_yield(df, **args)
    ref = pd.read_pickle(outpath)
    compare_dfs(ref, df)


@pytest.mark.parametrize(
    "inpath, spec, outpath",
    [
        (  # ts0 - dataframe with ufloats
            "xinxout.ufloat.df.pkl",
            [
                {"feedstock": "propane", "xin": "xin", "xout": "xout"},
            ],
            "Yp.ufloat.pkl",
        ),
    ],
)
def test_catalysis_yield_transform(inpath, spec, outpath, datadir):
    os.chdir(datadir)
    df = pd.read_pickle(inpath)
    print(df.head())
    transform(df, "catalysis.catalytic_yield", using=spec)
    ref = pd.read_pickle(outpath)
    print(ref.head())
    compare_dfs(ref, df)


@pytest.mark.parametrize(
    "inpath, spec, outkeys",
    [
        (  # ts0 - dataframe with ufloats
            "catalysis.xlsx",
            [
                {"feedstock": "propane", "element": "C", "xin": "xin", "xout": "xout"},
            ],
            ["Yp_C->CO2", "Yp_C->CO", "Yp_C->C3H6"],
        ),
    ],
)
def test_catalysis_yield_excel(inpath, spec, outkeys, datadir):
    os.chdir(datadir)
    df = pd.read_excel(inpath)
    transform(df, "catalysis.catalytic_yield", using=spec)
    for col in outkeys:
        pd.testing.assert_series_equal(df[col], df["r" + col], check_names=False)


def test_catalysis_yield_rinxin(datadir):
    os.chdir(datadir)
    df = pd.read_pickle("rinxin.pkl")
    catalysis.catalytic_yield(df, feedstock="CH4", xin="xin", xout="xout", output="Yp1")
    catalysis.catalytic_yield(df, feedstock="CH4", rin="nin", rout="nout", output="Yp2")
    df["nout->CH4"] = 0
    catalysis.catalytic_yield(df, feedstock="CH4", rin="nin", rout="nout", output="Yp3")
    for col in ["Yp1", "Yp2"]:
        assert np.allclose(
            df[f"{col}->CO"],
            np.array([0.01, 0.01, 0.009548, 0.010448, 0.01, 0.01]),
            atol=1e-6,
        ), f"yield of CO is wrong for {col}"
        assert np.allclose(
            df[f"{col}->CO2"],
            np.array([0.04, 0.09, 0.08593, 0.09403, 0.09, 0.09]),
            atol=1e-6,
        ), f"yield of CO2 is wrong for {col}"
    for col in ["Yp3"]:
        assert np.allclose(
            df[f"{col}->CO"],
            np.array([0.01, 0.01, 0.0095, 0.0105, 0.0101, 0.0099]),
            atol=1e-6,
        ), f"yield of CO is wrong for {col}"
        assert np.allclose(
            df[f"{col}->CO2"],
            np.array([0.04, 0.09, 0.0855, 0.0945, 0.0909, 0.0891]),
            atol=1e-6,
        ), f"yield of CO2 is wrong for {col}"
