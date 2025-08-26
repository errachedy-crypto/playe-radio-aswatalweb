import logging
import re

class CensoringFormatter(logging.Formatter):
    """
    Custom logging formatter that censors URLs and domain names in the
    final log message.
    """
    # This pattern matches full URLs (http/https) OR domain-like strings
    # with common TLDs found in the application's logs.
    _URL_PATTERN = re.compile(
        r'(?:https?://\S+|\S+\.(?:com|net|org|live|fm|tv|ua|ps|io|au|ch|git|mp3|m3u8))\S*'
    )

    def format(self, record):
        """
        Overrides the default format method. It first formats the original
        log record and then applies URL/domain censoring to the resulting string.
        """
        original_message = super().format(record)

        # Censor any URLs or domain names in the fully formatted message
        censored_message = self._URL_PATTERN.sub('xxx', original_message)

        return censored_message
