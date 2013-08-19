#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
This module contains the pyFlakes checker mode
"""
import _ast
from pyqode.core import CheckerMode, CheckerMessage, logger
from pyqode.core import MSG_STATUS_ERROR, MSG_STATUS_WARNING
from pyqode.core import CHECK_TRIGGER_TXT_SAVED


def pyflakesAnalysisProcess(q, codeString, filename, fileEncoding):
    msgs = []
    # First, compile into an AST and handle syntax errors.
    if not codeString or not fileEncoding:
        return
    try:
        tree = compile(codeString.encode(fileEncoding),
                       filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError as value:
        msg = value.args[0]
        (lineno, offset, text) = value.lineno, value.offset, value.text
        # If there's an encoding problem with the file, the text is None
        if text is None:
            # Avoid using msg, since for the only known case, it
            # contains a bogus message that claims the encoding the
            # file declared was unknown.s
            logger.warning("%s: problem decoding source" % filename)
        else:
            msgs.append(
                CheckerMessage(msg, MSG_STATUS_ERROR, lineno))
    else:
        # Okay, it's syntactically valid.  Now check it.
        from pyflakes import checker, messages
        msg_types = {messages.UnusedImport: MSG_STATUS_WARNING,
                     messages.RedefinedWhileUnused: MSG_STATUS_WARNING,
                     messages.RedefinedInListComp: MSG_STATUS_WARNING,
                     messages.ImportShadowedByLoopVar: MSG_STATUS_WARNING,
                     messages.ImportStarUsed: MSG_STATUS_WARNING,
                     messages.UndefinedName: MSG_STATUS_ERROR,
                     messages.DoctestSyntaxError: MSG_STATUS_ERROR,
                     messages.UndefinedExport: MSG_STATUS_ERROR,
                     messages.UndefinedLocal:  MSG_STATUS_ERROR,
                     messages.DuplicateArgument: MSG_STATUS_WARNING,
                     messages.Redefined: MSG_STATUS_WARNING,
                     messages.LateFutureImport: MSG_STATUS_WARNING,
                     messages.UnusedVariable: MSG_STATUS_WARNING}
        w = checker.Checker(tree, filename)
        w.messages.sort(key=lambda msg: msg.lineno)
        for warning in w.messages:
            msg = warning.message % warning.message_args
            line = warning.lineno
            status = msg_types[type(warning)]
            msgs.append(CheckerMessage(msg, status, line))
    q.put(msgs)


class PyFlakesCheckerMode(CheckerMode):
    DESCRIPTION = "Check python code using pyFlakes"
    IDENTIFIER = "pyFlakesCheckerMode"

    def __init__(self):
        CheckerMode.__init__(self, pyflakesAnalysisProcess,
                             delay=1200,
                             clearOnRequest=False)

    def _onInstall(self, editor):
        """
        Checks for pyflakes support. Auto disable if pyflakes could not be
        imported
        """
        CheckerMode._onInstall(self, editor)
        try:
            import pyflakes
        except ImportError:
            logger.warning("Cannot import PyFlakes, PyFlakesCheckerMode "
                            "disabled")
            self.enabled = False
