import pytest
import os
import pandas as pd
import uncertainties as uc
import dgpost

from .utils import compare_dfs, compare_images


@pytest.mark.parametrize(
    "inpath, tname, outpath",
    [
        (  # ts0 - load 1 dg, extract 2 keys directly
            "le_1.yaml",
            "table 1",
            "le_1.pkl",
        ),
        (  # ts1 - load 2 dgs, extract 2 tables with interpolation
            "le_2.yaml",
            "table 2",
            "le_2.pkl",
        ),
        (  # ts2 - load & extract, transform using catalysis.conversion
            "let_1.yaml",
            "df",
            "let_1.pkl",
        ),
        (  # ts3 - load & extract, multiple transforms
            "let_2.yaml",
            "df",
            "let_2.pkl",
        ),
        (  # ts4 - load & double extract, same index
            "lee_1.yaml",
            "df",
            "lee_1.pkl",
        ),
        (  # ts5 - load, extract, save in 4 formats
            "les_1.yaml",
            "table 1",
            "les_1.pkl",
        ),
        (  # ts6 - load, extract, save, strip sigma
            "les_2.yaml",
            "table 1",
            "les_2.pkl",
        ),
        (  # ts7 - load, extract and interpolate directly
            "lee_2a.yaml",
            "df",
            "lee_2.pkl",
        ),
        (  # ts8 - load, extract and interpolate via temp
            "lee_2b.yaml",
            "df",
            "lee_2.pkl",
        ),
    ],
)
def test_run(inpath, tname, outpath, datadir):
    os.chdir(datadir)
    dg, tab = dgpost.run(inpath)
    df = tab[tname]
    print(f"{df.head()=}")
    ref = pd.read_pickle(outpath)
    print(f"{ref.head()=}")
    df.to_pickle(outpath)
    compare_dfs(ref, df)


@pytest.mark.parametrize(
    "inpath, tname, outpath",
    [
        (  # ts0 - load & double extract, different index
            "lee_na.yaml",
            "df",
            "lee_na.pkl",
        )
    ],
)
def test_run_withna(inpath, tname, outpath, datadir):
    os.chdir(datadir)
    dg, tab = dgpost.run(inpath)
    df = tab[tname]
    print(f"{df.head()=}")
    ref = pd.read_pickle(outpath)
    print(f"{ref.head()=}")
    df.to_pickle(outpath)
    pd.testing.assert_frame_equal(ref.isna(), df.isna(), check_like=True)
    ref.fillna(uc.ufloat(0, 0))
    df.fillna(uc.ufloat(0, 0))
    pd.testing.assert_frame_equal(ref, df, check_like=True)
    assert ref.attrs == df.attrs


@pytest.mark.parametrize(
    "inpath, outpaths",
    [
        (  # ts0 - test saving to implicit formats
            "les_1.yaml",
            ["sparse.pkl", "sparse.json", "sparse.csv", "sparse.xlsx"],
        ),
        (
            # ts1 - test saving with explicit format and sigma = false
            "les_2.yaml",
            ["sparse.extension"],
        ),
    ],
)
def test_save(inpath, outpaths, datadir):
    os.chdir(datadir)
    dgpost.run(inpath)
    for of in outpaths:
        assert os.path.exists(of) and os.path.isfile(of)


@pytest.mark.parametrize(
    "inpath, tname, outpath, outfig",
    [
        (  # ts0 - two figures, select by top level, with legend
            "letp_1.yaml",
            "df",
            "letp_1.pkl",
            "letp_1.png",
        ),
        (  # ts1 - three figures, select via ->
            "lp_1.yaml",
            "df",
            "ref.electrochemistry_fe.ts0.pkl",
            "lp_1.png",
        ),
    ],
)
def test_run_with_plot(inpath, tname, outpath, outfig, datadir):
    os.chdir(datadir)
    dg, tab = dgpost.run(inpath)
    df = tab[tname]
    print(f"{df.head()=}")
    ref = pd.read_pickle(outpath)
    print(f"{ref.head()=}")
    df.to_pickle(outpath)
    compare_dfs(ref, df)
    compare_images("test.png", outfig)


@pytest.mark.parametrize(
    "inpath, patch, tname, outpath",
    [
        ("lee_2a.yaml", None, "df", "lee_2.pkl"),  # ts0
        ("lee_2c.yaml", "normalized.dg.json", "df", "lee_2.pkl"),  # ts1
        ("lee_2d.yaml", "sparse", "df", "lee_2.pkl"),  # ts2
    ],
)
def test_run_with_patch(inpath, patch, tname, outpath, datadir):
    os.chdir(datadir)
    dg, tab = dgpost.run(inpath, patch=patch)
    df = tab[tname]
    print(f"{df.head()=}")
    ref = pd.read_pickle(outpath)
    print(f"{ref.head()=}")
    df.to_pickle(outpath)
    compare_dfs(ref, df)
