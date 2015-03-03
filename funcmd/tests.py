import unittest
import funcmd.cmd

class FunCmdTest(unittest.TestCase):

    def test_get_environment(self):
        self.assertEqual(("lms.envs.dev", "lms"), funcmd.cmd.get_environment("edx.lms.dev"))
        self.assertEqual(("cms.envs.prod", "cms"), funcmd.cmd.get_environment("edx.cms.prod"))

        self.assertEqual(("fun.envs.lms.test", "lms"), funcmd.cmd.get_environment("lms.test"))

    def test_get_manage_command_arguments(self):
        self.assertIsNone(funcmd.cmd.get_manage_command_arguments("fun.envs.lms.test", "lms"))
        self.assertEqual(["runserver", "--traceback", "0.0.0.0:8000"],
                         funcmd.cmd.get_manage_command_arguments("fun.envs.lms.dev", "lms", "run", "--fast"))
