from pyqode.core import frontend, settings
from pyqode.python.frontend import modes


def get_mode(editor):
    return frontend.get_mode(editor, modes.PyIndenterMode)


def test_indent(editor):
    editor.clear()
    # empty doc
    mode = get_mode(editor)
    mode.indent()
    assert editor.toPlainText() == '    '
    editor.clear()
    editor.setPlainText('print("foo")')
    mode.indent()
    assert editor.toPlainText() == '    print("foo")'
    settings.use_spaces_instead_of_tabs = False
    editor.clear()
    mode.indent()
    assert editor.toPlainText() == '\t'
    settings.use_spaces_instead_of_tabs = True


def test_unindent(editor):
    editor.clear()
    # empty doc
    mode = get_mode(editor)
    mode.unindent()
    assert editor.toPlainText() == ''
    editor.clear()
    editor.setPlainText('    print("foo")')
    mode.unindent()
    assert editor.toPlainText() == 'print("foo")'
