# coding: utf-8

from stocker.dba import *

def test_Dba_init():
    assert Dba().client

def test_get_code_count_not_zero():
    assert 0 < Dba().get_code_count()

def test_get_code_iter_same_count():
    dba = Dba()
    assert dba.get_code_count = list(dba.get_code_iter())
