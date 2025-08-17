# -*- coding: utf-8 -*-

#   __
#  /__)  _  _     _   _ _/   _
# / (  (/ (/ (/ () ) )  /  _)
#          /

"""
Requests HTTP Library
~~~~~~~~~~~~~~~~~~~~~

Requests is an HTTP library, written in Python, for human beings.
Basically, how you would like HTTP to be. Behind the scenes, Requests uses
urllib3 to handle query sending and connection management.

    >>> import requests
    >>> r = requests.get('https://www.python.org')
    >>> r.status_code
    200
    >>> 'Python is a programming language' in r.text
    True

... or POST:

    >>> payload = dict(key1='value1', key2='value2')
    >>> r = requests.post('https://httpbin.org/post', data=payload)
    >>> print(r.text)
    {
      ...
      "form": {
        "key1": "value1",
        "key2": "value2"
      },
      ...
    }

The other HTTP methods are supported - see `requests.api`. Full documentation
is at <https://requests.readthedocs.io>.

:copyright: (c) 2012 by Kenneth Reitz.
:license: Apache 2.0, see LICENSE for more details.
"""

import warnings
import sys

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __build__, __author__, __author_email__, __license__
from .__version__ import __copyright__, __cake__

from . import utils
from . import packages
from .models import Request, Response, PreparedRequest
from .api import request, get, head, post, patch, put, delete, options
from .sessions import session, Session
from .status_codes import codes
from .exceptions import (
    RequestException,
    Timeout,
    URLRequired,
    TooManyRedirects,
    HTTPError,
    ConnectionError,
    FileModeWarning,
    ConnectTimeout,
    ReadTimeout,
    JSONDecodeError,
)

# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

# Prevent `pyopenssl`'s installation of `urllib3`'s `VerifiedHTTPSConnection`
# from causing connection issues in environments with custom CA bundles.
# See https://github.com/pyca/pyopenssl/pull/484
if packages.pyopenssl:
    try:
        from OpenSSL.SSL import SslError, SysCallError
        from .packages.urllib3.contrib.pyopenssl import (
            PyOpenSSLContext,
            extract_from_urllib3,
        )

        extract_from_urllib3()
    except (ImportError, AttributeError):
        pass

# The following code is to not break code that relies on the globally-scoped
# `urllib3.contrib.pyopenssl.extract_from_urllib3` call, which was removed in
# requests v2.26.0.
if packages.urllib3:
    target = f"{packages.urllib3.contrib.pyopenssl.__name__}.extract_from_urllib3"

    def extract_from_urllib3():
        warnings.warn(
            f"'{target}' has no effect and will be removed in a future version.",
            DeprecationWarning,
        )

    if packages.urllib3.contrib.pyopenssl:
        packages.urllib3.contrib.pyopenssl.extract_from_urllib3 = extract_from_urllib3

# The following code is to not break code that relies on the globally-scoped
# `urllib3.contrib.pyopenssl.inject_into_urllib3` call, which was removed in
# requests v2.26.0.
if packages.urllib3:
    target = f"{packages.urllib3.contrib.pyopenssl.__name__}.inject_into_urllib3"

    def inject_into_urllib3():
        warnings.warn(
            f"'{target}' has no effect and will be removed in a future version.",
            DeprecationWarning,
        )

    if packages.urllib3.contrib.pyopenssl:
        packages.urllib3.contrib.pyopenssl.inject_into_urllib3 = inject_into_urllib3


def check_compatibility(urllib3_version, chardet_version, charset_normalizer_version):
    urllib3_version = urllib3_version.split(".")
    assert urllib3_version != ["dev"]  # Verify urllib3 isn't a development version
    assert len(urllib3_version) == 2  # Verify urllib3 has a major and minor version
    assert urllib3_version[0].isdigit() and urllib3_version[1].isdigit()
    major, minor = int(urllib3_version[0]), int(urllib3_version[1])
    # Verify urllib3 isn't too old
    assert (major, minor) >= (1, 21)

    if chardet_version:
        chardet_version = chardet_version.split(".")
        assert chardet_version != ["dev"]
        assert len(chardet_version) == 3
        assert chardet_version[0].isdigit() and chardet_version[1].isdigit()
        major, minor, patch = (
            int(chardet_version[0]),
            int(chardet_version[1]),
            int(chardet_version[2]),
        )
        # chardet is optional, but if it's installed, it must be supported.
        # chardet < 3.0.2 is not supported by Requests.
        # chardet > 5.x is not supported by Requests.
        assert (3, 0, 2) <= (major, minor, patch) < (5, 0, 0)
    elif charset_normalizer_version:
        charset_normalizer_version = charset_normalizer_version.split(".")
        assert charset_normalizer_version != ["dev"]
        assert len(charset_normalizer_version) == 3
        assert (
            charset_normalizer_version[0].isdigit()
            and charset_normalizer_version[1].isdigit()
        )
        major, minor, patch = (
            int(charset_normalizer_version[0]),
            int(charset_normalizer_version[1]),
            int(charset_normalizer_version[2]),
        )
        # charset_normalizer is optional, but if it's installed, it must be supported.
        # charset_normalizer < 2.0.0 is not supported by Requests.
        assert (major, minor, patch) >= (2, 0, 0)
    else:
        # If neither chardet nor charset_normalizer are installed, that's fine.
        pass


# Check imported dependencies for compatibility.
try:
    check_compatibility(
        packages.urllib3.__version__,
        packages.chardet_version,
        packages.charset_normalizer_version,
    )
except (AssertionError, ValueError):
    # Don't raise this error if using a development version of requests.
    # We are in a development version if the 'dev' is in __version__.
    if "dev" not in __version__:
        raise ImportError("requests requirement missing") from None

# By now, we have verified that the dependencies are compatible, so we can
# always show the warning about the 'charset_normalizer'/'chardet' conflicts.
if packages.chardet_version and packages.charset_normalizer_version:
    warnings.warn(
        (
            f"You are using the 'charset_normalizer' package ({packages.charset_normalizer_version}) and the "
            f"'chardet' package ({packages.chardet_version}). Please use either "
            "the 'chardet' package or the 'charset_normalizer' package. "
            "They can't both be installed. To fix this, please uninstall "
            "one of them. For more information, see "
            "https://github.com/psf/requests/pull/6369."
        ),
        UserWarning,
    )
elif packages.chardet_version is None and packages.charset_normalizer_version is None:
    # We didn't mention this issue, but we must not let it happen either.
    warnings.warn(
        (
            "You are using a version of requests that is not compatible with "
            "the installed version of 'urllib3'. Please install the "
            "'charset_normalizer' package or the 'chardet' package. They "
            "can't both be missing. To fix this, please install one of "
            "them. For more information, see "
            "https://github.com/psf/requests/pull/6369."
        ),
        UserWarning,
    )
