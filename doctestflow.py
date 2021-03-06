import doctest
import string


class DocTestRunner(doctest.DocTestRunner):
    def report_failure(self, out, test, example, got):
        example.got = got

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


def get_output(example):
    o = getattr(example, 'got', example.want)
    o = [
        (s if s.strip() else '<BLANKLINE>\n')
        for s in o.splitlines(True)
    ]

    def strip_tracebacks(o):
        o = iter(o)
        while 1:
            x = next(o)
            yield x

            if x.strip() == 'Traceback (most recent call last):':
                while 1:
                    x = next(o)
                    if x[:1] not in string.whitespace:
                        yield x
                        break

    o = list(strip_tracebacks(o))

    return ''.join(o)


def generate_doctest(test):
    output = []
    out = output.append

    for example in test.examples.all_items:
        if isinstance(example, doctest.Example):
            prefix = ' ' * example.indent
            outp = lambda s: out(indent(s, prefix))
            outp('>>> ' + '... '.join(example.source.splitlines(True)))
            outp(get_output(example))
        else:
            out(str(example))

    return ''.join(output)


# Pulled in from Python 3.4 `textwrap` module
def indent(text, prefix, predicate=None):
    if predicate is None:
        def predicate(line):
            return line.strip()

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if predicate(line) else line)
    return ''.join(prefixed_lines())