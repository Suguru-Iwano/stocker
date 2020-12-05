# coding: utf-8

import os
import pytest

from stocker.stkdaily_p import *


def test_publish_none_message():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), None)


def test_publish2_yes_message():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), 'message')


def test_publish_err1():
    with pytest.raises(FatalException):
        publish('', 'topic', None)


def test_publish_err2():
    with pytest.raises(FatalException):
        publish('project', None, None)
