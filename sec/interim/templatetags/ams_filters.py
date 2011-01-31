from django import template

register = template.Library()

@register.filter
def abbr_status(value):
    """
    Converts RFC Status to a short abbreviation
    """
    d = {'Proposed Standard':'PS',
         'Draft Standard':'DS',
	 'Standard':'S',
	 'Historic':'H',
	 'Informational':'I',
	 'Experimental':'E'}

    #assert False, (value, d.get(value,value))
    return d.get(value,value)
