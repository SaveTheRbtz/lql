# vim:fileencoding=utf8
from contextlib import contextmanager

@contextmanager
def attention(fill='=', width=80, text=' ERROR '):
    """Prints header and footer between data"""
    print "{text:{fill}^{width}}".format(text=text, width=width, fill=fill)
    yield
    print fill * width
