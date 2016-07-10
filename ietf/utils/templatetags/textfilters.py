from __future__ import unicode_literals

from django.template.base import Library
from django.template.defaultfilters import stringfilter

from ietf.utils.text import xslugify as _xslugify

register = Library()

@register.filter(is_safe=True)
@stringfilter
def xslugify(value):
    """
    Converts to ASCII. Converts spaces to hyphens. Removes characters that
    aren't alphanumerics, underscores, slashes, or hyphens. Converts to
    lowercase.  Also strips leading and trailing whitespace.
    """
    return _xslugify(value)
