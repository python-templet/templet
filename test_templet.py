#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import re
import sys
import traceback
import unittest


import templet as m

templet = m.templet
func_code = m.func_code


class Template:

    @templet
    def hello(self, name):
        r"Hello $name."

    @templet
    def add(self, a, b):
        r"$a + $b = ${a + b}"

    @templet
    def hello_list(self, a):
        r"""${[self.hello(x) for x in a]}"""

    @templet
    def repeat(self, a, count=5): """\
        ${{ if count == 0: return '' }}
        $a${self.repeat(a, count - 1)}"""

    @templet
    def black_stars(self, count=4): """\
        ${{ if not count: return '' }}
        \N{BLACK STAR}${self.black_stars(count - 1)}"""

    @staticmethod
    @templet
    def quotes():
        """($$ $.$($/$'$")"""

    @templet
    def indented(self, x):
        '''\
        $
           var val
           x   $x
        '''

    @templet
    def html_cell_concat_values(self, name, values):
        '''\
        <tr><td>$name</td><td>${{
             for val in values:
                 out.append(str(val))
        }}</td></tr>
        '''

    @templet
    def multiline_countdown(self, n):
        '''\
        $n
        ${{
        if n > 1:
            out.append(self.multiline_countdown(n - 1))
        }}'''


def line_of_exception():
    return traceback.extract_tb(sys.exc_info()[2], 10)[-1][1]


def line_of_syntax_error(e):
    assert isinstance(e, SyntaxError)
    return int(re.search('line ([0-9]*)', str(e)).group(1))


def first_line(func):
    return func_code(func).co_firstlineno


class Test(unittest.TestCase):

    @property
    def template(self):
        return Template()

    def test_variable(self):
        self.assertEqual("Hello Henry.", self.template.hello('Henry'))

    def test_expr(self):
        self.assertEqual("1 + 2 = 3", self.template.add(1, 2))

    def test_recursion(self):
        self.assertEqual("foofoofoofoofoo", self.template.repeat('foo'))
        self.assertEqual("foofoo", self.template.repeat('foo', 2))

    def test_quotes(self):
        self.assertEqual("""($ $.$($/$'$")""", self.template.quotes())

    def test_unicode(self):
        self.assertEqual(
            "\N{BLACK STAR}" * 10,
            self.template.black_stars(count=10))

    def test_indented(self):
        self.assertEqual(
            "   var val\n   x   11\n",
            self.template.indented(11))

    def test_list_comprehension(self):
        self.assertEqual(
            "Hello David.Hello Kevin.",
            self.template.hello_list(['David', 'Kevin']))

    def test_code_block(self):
        self.assertEqual(
            "<tr><td>prices</td><td>123</td></tr>\n",
            self.template.html_cell_concat_values('prices', [1, 2, 3]))

    def test_multiline_code_block(self):
        self.assertEqual('4\n3\n2\n1\n', self.template.multiline_countdown(4))

    def test_syntax_error(self):
        error_line = 0
        #
        try:
            def marker(): pass         # 0

            @templet                   # 2
            def testsyntaxerror():     # 3
                # extra line here      # 4
                # another extra line here
                '''
                some text
                $a$<'''                # 8
        except SyntaxError as e:
            error_line = line_of_syntax_error(e)
        #
        self.assertEqual(first_line(marker) + 8, error_line)

    def test_syntax_error_with_continuation(self):
        error_line = 0
        #
        try:
            def marker(): pass         # 0

            @templet                   # 2
            def testsyntaxerror():     # 3
                # extra line here      # 4
                # another extra line here
                '''\
                some text
                $a$<'''                # 8
        except SyntaxError as e:
            error_line = line_of_syntax_error(e)
        #
        self.assertEqual(first_line(marker) + 8, error_line)

    def test_syntax_error_in_multiline_code_block(self):
        error_line = 0
        #
        try:
            def marker(): pass         # 0

            @templet                   # 2
            def testsyntaxerror(): ''' # 3
                ${{                    # 4
                -                      # 5
                }}                     # 6
                '''
        except SyntaxError as e:
            error_line = line_of_syntax_error(e)
        #
        self.assertEqual(first_line(marker) + 5, error_line)

    def test_runtime_error(self):
        error_line = 0

        def marker(): pass             # 0

        @templet                       # 2
        def testruntimeerror(a):       # 3
            '''
            some $a text               # 5
            ${{                        # 6
                out.append(a) # just using up more lines
            }}                         # 8
            some more text             # 9
            $b text $a again'''        # 10
        self.assertEqual(
            first_line(marker) + 2,
            first_line(testruntimeerror))
        #
        try:
            testruntimeerror('hello')
        except NameError:
            error_line = line_of_exception()
        #
        self.assertEqual(first_line(marker) + 10, error_line)

    def test_runtime_error_leading_slash(self):
        error_line = 0

        def marker(): pass             # 0

        @templet                       # 2
        def testruntimeerror(a):       # 3
            '''\
            some $a text               # 5
            ${{                        # 6
                out.append(a) # just using up more lines
            }}                         # 8
            some more text             # 9
            $b text $a again'''        # 10
        self.assertEqual(
            first_line(marker) + 2,
            first_line(testruntimeerror))
        #
        try:
            testruntimeerror('hello')
        except NameError:
            error_line = line_of_exception()
        #
        self.assertEqual(first_line(marker) + 10, error_line)

    def test_nosource(self):
        l = {}
        exec(
            """if True:
            @templet
            def testnosource(a):
                "${[c for c in reversed(a)]} is '$a' backwards."
            """, globals(), l)
        self.assertEqual(
            "olleh is 'hello' backwards.",
            eval('testnosource("hello")', globals(), l))

    def test_nosource_error_line(self):
        error_line = None
        try:
            exec("""if True:
                @templet
                def testnosource_error(a):
                    "${[c for c in reversed a]} is '$a' backwards."
                """, globals(), {})
        except SyntaxError as e:
            error_line = line_of_syntax_error(e)
        self.assertEqual(4, error_line)


def main():
    print('\n' * 3)
    print('  *  ' * 16)
    print('\n' * 3)

    def run(cmd):
        print(cmd)
        if os.system(cmd):
            sys.exit(1)
    for src in ('templet.py', 'test_templet.py'):
        run('env/bin/flake8 --ignore E701 ' + src)
    for python in (
            'python2',
            'python3',
            'pypy-4.0.1-linux_x86_64-portable/bin/pypy',
            'pypy3-2.4-linux_x86_64-portable/bin/pypy3'):
        run(python + ' -m unittest test_templet')


if __name__ == '__main__':
    main()
