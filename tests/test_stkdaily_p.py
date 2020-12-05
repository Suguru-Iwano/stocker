# coding: utf-8

import os

from stocker.stkdaily_p import *


def test_publish1():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), None)


def test_publish2():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), 'message')


def test_publish_err1():
    try:
        publish('', 'topic', None)
    except FatalException:
        assert True
    else:
        assert False


def test_publish_err2():
    try:
        publish('project', None, None)
    except FatalException:
        assert True
    else:
        assert False
