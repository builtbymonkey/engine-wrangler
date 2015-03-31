from enginewrangler.formatters.base import FormatterBase
from enginewrangler.vendor.simplexmlwriter import XMLWriter, escape_cdata
from enginewrangler.valuetypes import *

class XmlFormatter(FormatterBase):
    name = 'xml'

    def __init__(self, out):
        self._outfile = out
        self._out = XMLWriter(self._outfile)

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
        if isinstance(value, HtmlString):
            self._outfile.write(
                '<%s><![CDATA[' % escape_cdata(name)
            )

            value = ' '.join(
                value.replace(
                    '&nbsp;', ' '
                ).splitlines()
            )

            while '  ' in value:
                value = value.replace('  ', ' ')

            self._outfile.write(value)

            self._outfile.write(
                ']]></%s>' % escape_cdata(name)
            )
        elif isinstance(value, bool):
            self._out.element(
                unicode(str(name).decode('utf-8')),
                value and 'true' or 'false'
            )
        elif not value is None:
            self._out.element(
                unicode(str(name).decode('utf-8')),
                unicode(str(value).decode('utf-8'))
            )
