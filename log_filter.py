import logging
import re

class URLFilter(logging.Filter):
    """
    A logging filter that censors URLs in log records to prevent them from
    being written to the log file.
    """
    def __init__(self, name=''):
        super().__init__(name)
        # This regex will find http/https urls
        self.url_pattern = re.compile(r'https?://\S+')

    def _censor(self, text):
        """
        Replaces any URL found in the given text with 'xxx'.
        """
        if not isinstance(text, str):
            return text
        return self.url_pattern.sub('xxx', text)

    def filter(self, record):
        """
        Applies the censor to the log record's message and arguments.
        """
        record.msg = self._censor(record.msg)
        if record.args:
            record.args = tuple(self._censor(arg) for arg in record.args)
        return True