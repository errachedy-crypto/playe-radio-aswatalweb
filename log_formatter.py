import logging
import re

class CensoringFormatter(logging.Formatter):
    """
    Custom logging formatter that censors URLs in the final log message,
    ensuring that URLs from all sources (including third-party libraries)
    are redacted.
    """
    _URL_PATTERN = re.compile(r'https?://\S+')

    def format(self, record):
        """
        Overrides the default format method. It first formats the original
        log record and then applies URL censoring to the resulting string.
        """
        # Let the parent class format the message
        original_message = super().format(record)

        # Censor any URLs in the fully formatted message
        censored_message = self._URL_PATTERN.sub('xxx', original_message)

        return censored_message
