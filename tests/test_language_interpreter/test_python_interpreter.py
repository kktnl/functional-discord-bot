from unittest import TestCase


class TestPyCmd(TestCase):

    test_p = PyCmd()
    test_exec = "print('Hello World!')"
    text_eval = "7+5"
    test_mixed = """print('Hello World!')\n7+5"""

    @unittest.skip('may skip whole idea')
    def test_run_the_file(self):
        test_only_exec = test_p.run_the_file(test_exec)
        self.assertEqual(
                test_only_exec,
                "Hello World!"
        )

        test_only_eval = test_p.run_the_file(test_eval)
        self.assertEqual(
                test_only_eval,
                "#EVALUATION RESULT# :  12"
        )

        test_mixed_input = test_p.run_the_file(test_mixed)
        self.assertEqual(
                test_mixed_input,
                """Hello World!\n
                #EVALUATION RESULT# : 12"""
        )




