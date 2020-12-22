# coding: utf-8

import os

import pytest
from stocker.stkdaily_p import (ENV_KEY_PROJECT, ENV_KEY_TOPIC, FatalException,
                                publish)


def test_publish_none_message():
    publish(os.getenv(ENV_KEY_PROJECT) or '',
            os.getenv(ENV_KEY_TOPIC) or '', None)


def test_publish_yes_message():
    publish(os.getenv(ENV_KEY_PROJECT) or '',
            os.getenv(ENV_KEY_TOPIC) or '', 'message')


def test_publish_err_no_project():
    with pytest.raises(FatalException):
        publish('', 'topic', 'message')


def test_publish_err_no_topic():
    with pytest.raises(FatalException):
        publish('project', '', 'message')
