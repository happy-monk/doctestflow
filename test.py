import io
import sys
from contextlib import contextmanager
from textwrap import dedent
import doctest
import unittest
import doctestflow


@contextmanager
def capture_output():
    _stdout = sys.stdout
    sys.stdout = io.StringIO() if sys.version_info[0] == 3 else io.BytesIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = _stdout


class DoctestFlowTests(unittest.TestCase):
    def check(self, src, ref_generated, test_generated_doctest = True):
        src = dedent(src)
        ref_generated = dedent(ref_generated)

        parser = doctestflow.DocTestParser()
        runner = doctestflow.DocTestRunner()

        test = parser.get_doctest(src, {}, '__main__', '__main__', 1)
        runner.run(test)

        generated = doctestflow.generate_doctest(test)
        self.assertMultiLineEqual(ref_generated, generated)

        if test_generated_doctest:
            parser = doctest.DocTestParser()
            runner = doctest.DocTestRunner()
            test = parser.get_doctest(generated, {}, '__main__', '__main__', 1)
            result = runner.run(test)
            self.assertEqual(result.failed, 0)

    def test_simple_doctests(self):
        self.check('''
            >>> 2+2
            >>> 3**4
        ''','''
            >>> 2+2
            4
            >>> 3**4
            81
        ''')

        self.check('''
            >>> 2+2
            5
            >>> 3**4
            48
        ''','''
            >>> 2+2
            4
            >>> 3**4
            81
        ''')


    def test_simple_doctest_with_docstrings(self):
        self.check('''
            The interpreter acts as a simple calculator: you can type an expression at it
and it will write the value.

                >>> 2+2
                >>> 50 - 5*6
                >>> (50 - 5*6) // 4

            With Python, it is possible to use the ``**`` operator to calculate powers [#]_::

               >>> 5 ** 2  # 5 squared
               >>> 2 ** 7  # 2 to the power of 7
        ''','''
            The interpreter acts as a simple calculator: you can type an expression at it
and it will write the value.

                >>> 2+2
                4
                >>> 50 - 5*6
                20
                >>> (50 - 5*6) // 4
                5

            With Python, it is possible to use the ``**`` operator to calculate powers [#]_::

               >>> 5 ** 2  # 5 squared
               25
               >>> 2 ** 7  # 2 to the power of 7
               128
        ''')

    def test_blanklines_between_tests(self):
        self.check('''
            >>> 1+1
            >>> 2+2



            >>> 2**6; 3**4
            64

            >>> 10//2
        ''','''
            >>> 1+1
            2
            >>> 2+2
            4



            >>> 2**6; 3**4
            64
            81

            >>> 10//2
            5
        ''')

    def test_indents(self):
        self.check('''
            >>> 2+3
                 >>> 3*2

              >>> 7*7
        ''','''
            >>> 2+3
            5
                 >>> 3*2
                 6

              >>> 7*7
              49
        ''')

    def test_multiline_source(self):
        self.check('''
            >>> for x in range(3):
            ...     (x+2)**2
        ''','''
            >>> for x in range(3):
            ...     (x+2)**2
            4
            9
            16
        ''')

    def test_ellipsis(self):
        self.check('''
            >>> 2*2
            5
            >>> list(range(1, 6)) # doctest: +ELLIPSIS
            [1, ..., 5]
        ''','''
            >>> 2*2
            4
            >>> list(range(1, 6)) # doctest: +ELLIPSIS
            [1, ..., 5]
        ''')

    def test_exceptions(self):
        self.check('''
            >>> int('x')
            Traceback (most recent call last):
            xxx

            >>> [][0]
            Traceback (most recent call last):
            xxx
        ''','''
            >>> int('x')
            Traceback (most recent call last):
            ValueError: invalid literal for int() with base 10: 'x'

            >>> [][0]
            Traceback (most recent call last):
            IndexError: list index out of range
        ''')

    def test_unexpected_exceptions(self):
        test = '''
            >>> x = 0 #5
            >>> 1/x
        '''

        # unexpected exceptions should not be showed in generated doctest
        with capture_output() as output:
            self.check(test, test, test_generated_doctest = False)

        self.assertIn(dedent('''
            Failed example:
                1/x
            Exception raised:
        '''), output.getvalue())

    def test_mismatching_exceptions(self):
        self.check('''
            >>> [][0]
            Traceback (most recent call last):
            ZeroDivisionError: xxx
        ''','''
            >>> [][0]
            Traceback (most recent call last):
            IndexError: list index out of range
        ''')

    def test_blanklines_in_output(self):
        self.check('''
            >>> 1; print(''); 42
            >>> print(' ');print(' ');print('')
        ''','''
            >>> 1; print(''); 42
            1
            <BLANKLINE>
            42
            >>> print(' ');print(' ');print('')
            <BLANKLINE>
            <BLANKLINE>
            <BLANKLINE>
        ''')
