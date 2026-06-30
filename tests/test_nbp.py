import pandas as pd
import pytest

from sources.nbp import NBPCurrent, NBPHistorySource
from tests.constances import NBP_HISTORY_DATA, TEST_DATA


@pytest.fixture
def nbp_current():
    yield NBPCurrent(table='A')

@pytest.fixture
def nbp_history_source():
    yield NBPHistorySource(table='A')

def test_transform_data_to_df_history(nbp_history_source):
    result = nbp_history_source.transform_data_to_df(data=NBP_HISTORY_DATA)
    assert isinstance(result, pd.DataFrame)

def test_transform_data_to_df_history_ValueError(nbp_history_source):
    with pytest.raises(ValueError):
        nbp_history_source.transform_data_to_df(data=None)

def test_transform_data_to_df(nbp_current):
    result = nbp_current.transform_data_to_df(data=TEST_DATA)
    assert isinstance(result, pd.DataFrame)

def test_transform_data_to_df_ValueError(nbp_current):
    with pytest.raises(ValueError):
        nbp_current.transform_data_to_df(data=None)


