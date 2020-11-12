#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals

import sys

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu, leftrec, nomemo
from tatsu.parsing import leftrec, nomemo  # noqa
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {}  # type: ignore


class tlBuffer(Buffer):
    def __init__(
        self,
        text,
        whitespace=None,
        nameguard=None,
        comments_re=None,
        eol_comments_re=None,
        ignorecase=None,
        namechars='',
        **kwargs
    ):
        super(tlBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class tlParser(Parser):
    def __init__(
        self,
        whitespace=None,
        nameguard=None,
        comments_re=None,
        eol_comments_re=None,
        ignorecase=None,
        left_recursion=True,
        parseinfo=True,
        keywords=None,
        namechars='',
        buffer_class=tlBuffer,
        **kwargs
    ):
        if keywords is None:
            keywords = KEYWORDS
        super(tlParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            parseinfo=parseinfo,
            keywords=keywords,
            namechars=namechars,
            buffer_class=buffer_class,
            **kwargs
        )

    @tatsumasu()
    @nomemo
    def _start_(self):  # noqa
        self._phi_()
        self._check_eof()

    @tatsumasu()
    @leftrec
    def _phi_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('(')
                self._phi_()
                self.name_last_node('phi1')
                self._token(')')
            with self._option():
                self._token('~')
                self.name_last_node('op')
                self._phi_()
                self.name_last_node('phi1')
            with self._option():
                self._quantifier_()
                self.name_last_node('mod')
                self._phi_()
                self.name_last_node('phi1')
            with self._option():
                self._unarymod_()
                self.name_last_node('mod')
                self._phi_()
                self.name_last_node('phi1')
            with self._option():
                self._phi_()
                self.name_last_node('phi1')
                self._boolop_()
                self.name_last_node('op')
                self._phi_()
                self.name_last_node('phi2')
            with self._option():
                self._phi_()
                self.name_last_node('phi1')
                self._binarymod_()
                self.name_last_node('mod')
                self._phi_()
                self.name_last_node('phi2')
            with self._option():
                self._atom_()
                self.name_last_node('phi1')
            self._error('no available options')
        self.ast._define(
            ['mod', 'op', 'phi1', 'phi2'],
            []
        )

    @tatsumasu()
    def _boolop_(self):  # noqa
        with self._choice():
            with self._option():
                self._token('&')
            with self._option():
                self._token('|')
            with self._option():
                self._token('=>')
            with self._option():
                self._token('<=>')
            self._error('no available options')

    @tatsumasu()
    def _quantifier_(self):  # noqa
        self._pattern('[AE]')
        self.name_last_node('op')

        def block1():
            self._token('{')
            self._actions_()
            self.name_last_node('act')
            self._token('}')
        self._closure(block1)
        self.ast._define(
            ['act', 'op'],
            []
        )

    @tatsumasu()
    def _unarymod_(self):  # noqa
        self._pattern('[XFG]')
        self.name_last_node('op')

        def block1():
            self._token('{')
            self._actions_()
            self.name_last_node('act')
            self._token('}')
        self._closure(block1)
        self.ast._define(
            ['act', 'op'],
            []
        )

    @tatsumasu()
    def _binarymod_(self):  # noqa

        def block0():
            self._token('{')
            self._actions_()
            self.name_last_node('act1')
            self._token('}')
        self._closure(block0)
        self._pattern('[UR]')
        self.name_last_node('op')

        def block3():
            self._token('{')
            self._actions_()
            self.name_last_node('act2')
            self._token('}')
        self._closure(block3)
        self.ast._define(
            ['act1', 'act2', 'op'],
            []
        )

    @tatsumasu()
    def _atom_(self):  # noqa
        self._pattern('\\b(\\w+|"[^\\"]+"|\'[^\\\']+\')\\b')

    @tatsumasu()
    def _actions_(self):  # noqa

        def sep0():
            self._token(',')

        def block0():

            def block1():
                self._token('~')
            self._closure(block1)
            self._atom_()
        self._gather(block0, sep0)


class tlSemantics(object):
    def start(self, ast):  # noqa
        return ast

    def phi(self, ast):  # noqa
        return ast

    def boolop(self, ast):  # noqa
        return ast

    def quantifier(self, ast):  # noqa
        return ast

    def unarymod(self, ast):  # noqa
        return ast

    def binarymod(self, ast):  # noqa
        return ast

    def atom(self, ast):  # noqa
        return ast

    def actions(self, ast):  # noqa
        return ast


def main(filename, start=None, **kwargs):
    if start is None:
        start = 'start'
    if not filename or filename == '-':
        text = sys.stdin.read()
    else:
        with open(filename) as f:
            text = f.read()
    parser = tlParser()
    return parser.parse(text, rule_name=start, filename=filename, **kwargs)


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, tlParser, name='tl')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(asjson(ast), indent=2))
    print()
