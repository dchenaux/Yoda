from jinja2 import escape
import pprint
import os


def pluralize(word, count):
    if count <= 1:
        return word
    else:
        return word + 's'
    # if end_ptr and str.endswith(end_ptr):
    #     return str[:-1*len(end_ptr)]+rep_ptr
    # else:
    #     return str+'s'


def format_stack_trace(value):
    stack_trace = []
    fmt = (
        '<span class="path">{0}/</span>'
        '<span class="file">{1}</span> in <span class="func">{3}</span>'
        '(<span class="lineno">{2}</span>) <span class="code">{4}</span>'
    )
    for frame in value:
        params = map(escape, frame[0].rsplit('/', 1) + list(frame[1:]))
        stack_trace.append(fmt.format(*params))
    return '\n'.join(stack_trace)


def embolden_file(path):
    head, tail = os.path.split(escape(path))
    return os.sep.join([head, '<strong>{0}</strong>'.format(tail)])


def format_dict(value, width=60):
    return pprint.pformat(value, width=int(width))


def highlight(value, language):
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
    except ImportError:
        return value
    # Can't use class-based colouring because the debug toolbar's css rules
    # are more specific so take precedence
    formatter = HtmlFormatter(style='friendly', nowrap=True, noclasses=True)
    return highlight(value, get_lexer_by_name(language), formatter)
