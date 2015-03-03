class FormatterBase(object):
    name = 'base'

    def __init__(self, out):
        self._out = out

    def start_document(self):
        pass

    def end_document(self):
        pass

    def start_section(self, name):
        raise NotImplementedError('Method not implemented.')

    def end_section(self, name = None):
        raise NotImplementedError('Method not implemented.')

    def property(self, name, value):
        raise NotImplementedError('Method not implemented.')
