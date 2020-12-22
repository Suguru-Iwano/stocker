# coding: utf-8

from stocker.dba import Dba
from google.cloud.bigquery.table import RowIterator


def test_Dba_init():
    assert Dba().client


def test_get_code_iter_same_count():
    dba = Dba()
    result = dba.get_code_iter()
    assert type(result) is RowIterator
    assert 0 <= result.total_rows
