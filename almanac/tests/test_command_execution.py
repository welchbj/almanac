"""Tests for execution of various command lines."""

from almanac.errors.arguments.no_such_argument_error import NoSuchArgumentError
from unittest import IsolatedAsyncioTestCase

from .utils import AlmanacTextMixin


class TestCommandExecution(IsolatedAsyncioTestCase, AlmanacTextMixin):

    async def test_simple_type_promotion(self):
        app = self.get_test_app()
        app.add_promoter_for_type(int, bool)

        @app.cmd.register()
        async def cmd(arg: int):
            self.assertEquals(type(arg), bool)
            self.assertEquals(arg, True)

        await app.eval_line('cmd arg=1')

    async def test_var_args_type_promotions(self):
        app = self.get_test_app()
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

    async def test_missing_pos_args(self):
        # TODO
        assert False

    async def test_missing_kw_args(self):
        # TODO
        assert False

    async def test_too_many_pos_args(self):
        # TODO
        assert False

    async def test_extra_kw_args(self):
        app = self.get_test_app()

        @app.cmd.register()
        @app.arg.a(name='A')
        async def some_command(a: int, b: str, x: bool = False):
            pass

        with self.assertRaises(NoSuchArgumentError) as ctx:
            await app.eval_line('some_command a=1 b="a string" x=False')
        self.assertTupleEqual(ctx.exception.names, ('a',))

        with self.assertRaises(NoSuchArgumentError) as ctx:
            await app.eval_line('some_command A=1 a=1 b="a string" x=False')
        self.assertTupleEqual(ctx.exception.names, ('a',))

        with self.assertRaises(NoSuchArgumentError) as ctx:
            await app.eval_line('some_command A=1 b=2 c=3 x=True y=4 z=[1,2,3]')
        self.assertTupleEqual(ctx.exception.names, ('c', 'y', 'z',))
