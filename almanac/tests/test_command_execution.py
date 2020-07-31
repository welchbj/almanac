"""Tests for execution of various command lines."""

from unittest import IsolatedAsyncioTestCase

from almanac import Application


class TestCommandExecution(IsolatedAsyncioTestCase):

    async def test_simple_type_promotion(self):
        app = Application()
        app.add_promoter_for_type(int, bool)

        @app.cmd.register()
        async def cmd(arg: int):
            self.assertEquals(type(arg), bool)
            self.assertEquals(arg, True)

        await app.eval_line('cmd arg=1')

    async def test_var_args_type_promotions(self):
        app = Application()
        app.add_promoter_for_type(int, str)

        @app.cmd.register()
        async def cmd_var_pos_args(*args: int):
            for i, x in enumerate(args):
                self.assertEquals(type(x), str)
                self.assertEquals(x, str(i))

        await app.eval_line('cmd_var_pos_args 0 1 2 3 4 5')

        @app.cmd.register()
        async def cmd_var_kw_args(**kwargs: int):
            for key, val in kwargs.items():
                self.assertEquals(type(val), str)
                self.assertEquals(val, '18')

        await app.eval_line('cmd_var_kw_args one=18 two=18 three=18')
