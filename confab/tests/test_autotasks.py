"""
Tests for template generation.
"""
from unittest import TestCase
from fabric.api import env
from fabric.state import commands
from os.path import dirname, join
from nose.tools import eq_, ok_
from mock import patch, Mock

from confab.autotasks import generate_tasks


class TestAutoTasks(TestCase):

    def setUp(self):
        # create tasks
        self.settings = generate_tasks(join(dirname(__file__), "data/autotasks"))

    def tearDown(self):
        if "environmentdef" in env:
            del env["environmentdef"]

    def test_environment_autotask(self):
        """
        Calling generate_tasks() creates a task that loads each environment.
        """
        for environment in self.settings.environmentdefs.iterkeys():
            task = commands[environment]

            ok_("environmentdef" not in env)
            task()
            ok_("environmentdef" in env)
            environmentdef = env.environmentdef
            eq_(environment, environmentdef.name)
            del env["environmentdef"]

    def test_idempotency(self):
        """
        Environment tasks are idempotent (as long as no other environment is loaded)
        """
        task = commands["local"]
        task()
        task()

    def test_mismatch(self):
        """
        Environment tasks for different environments cannot be used together.
        """
        error = Mock()
        error.side_effect = Exception("abort")

        with patch("confab.autotasks.abort", error):
            local = commands["local"]
            local()
            other = commands["other"]

            with self.assertRaises(Exception) as capture:
                other()
            eq_("abort", capture.exception.message)
