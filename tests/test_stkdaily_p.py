# coding: utf-8

import os
import pytest

from stocker.stkdaily_p import *


def test_publish_none_message():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), None)


def test_publish_yes_message():
    publish(os.getenv(ENV_KEY_PROJECT), os.getenv(ENV_KEY_TOPIC), 'message')


def test_publish_err_no_project():
    with pytest.raises(FatalException):
        publish('', 'topic', 'message')


def test_publish_err_no_topic():
    with pytest.raises(FatalException):
        publish('project', '', 'message')
