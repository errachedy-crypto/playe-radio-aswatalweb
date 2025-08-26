import logging
import re

class CensoringFormatter(logging.Formatter):
    """
    Custom logging formatter that censors URLs in the final log message.
    """
    _URL_PATTERN = re.compile(r'https?://\S+')

    def format(self, record):
        """
        Overrides the default format method to censor the final string.
        """
        original_message = super().format(record)
        censored_message = self._URL_PATTERN.sub('xxx', original_message)
        return censored_message