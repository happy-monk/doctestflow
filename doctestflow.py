import doctest
from textwrap import indent


class DocTestRunner(doctest.DocTestRunner):
    def report_failure(self, out, test, example, got):
        example.got = got

    def report_unexpected_exception(self, out, test, example, exc_info):
        exc_type, exc, _ = exc_info
        got = 'Traceback (most recent call last):\n' + exc_type.__name__
        msg = str(exc)
        if msg:
            got += ': ' + msg
        example.got = got + '\n'

class List(list):
    pass


class DocTestParser(doctest.DocTestParser):
    def get_examples(self, *a, **kw):
        items = self.parse(*a, **kw)
        examples = List([
            x for x in items
            if isinstance(x, doctest.Example)
        ])
        examples.all_items = items
        return examples


def generate_doctest(test):
    output = []
    out = output.append

    for example in test.examples.all_items:
        if isinstance(example, doctest.Example):
            prefix = ' ' * example.indent
            outp = lambda s: out(indent(s, prefix))
            outp('>>> ' + example.source)
            outp(getattr(example, 'got', example.want))
        else:
            out(str(example))

    return ''.join(output)
