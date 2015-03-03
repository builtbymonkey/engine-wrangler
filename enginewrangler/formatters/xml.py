from enginewrangler.formatters.base import FormatterBase
from enginewrangler.vendor.simplexmlwriter import XMLWriter

class XmlFormatter(FormatterBase):
    name = 'xml'

    def __init__(self, out):
        self._out = XMLWriter(out)

    def start_document(self):
        self._out.declaration()
        self._out.start('document')

    def end_document(self):
        self._out.end()

    def start_section(self, name):
        self._out.start(name)

    def end_section(self, name = None):
        if name:
            self._out.end(name)
        else:
            self._out.end()

    def property(self, name, value):
        self._out.element(
            unicode(str(name).decode('utf-8')),
            unicode(str(value).decode('utf-8'))
        )
