from django import template

register = template.Library()



# returns the a dictioary's value from it's key.
@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''

@register.filter(name='get_id')
def get_id(room,day):
    date = ""
    print "getid"
    print " "
    from ietf.meeting.models import TimeSlot
    print "ROOM=", room
    print "date=", date
    x = TimeSlot.objects.filter(time=date)
    return "bla"

# returns the length of the value of a dict.
# We are doing this to how long the title for the calendar should be. (this should return the number of time slots)
@register.filter(name='colWidth')
def get_col_width(dict, index):
    if index in dict:
        return len(dict[index])
    return 0

# Replaces characters that are not acceptable html ID's
@register.filter(name='to_acceptable_id')
def to_acceptable_id(inp):
    # see http://api.jquery.com/category/selectors/?rdfrom=http%3A%2F%2Fdocs.jquery.com%2Fmw%2Findex.php%3Ftitle%3DSelectors%26redirect%3Dno
    # for more information.
    invalid = ["!","\"", "#","$","%","&","'","(",")","*","+",",",".","/",":",";","<","=",">","?","@","[","\\","]","^","`","{","|","}","~"," "]
    out = str(inp)
    for i in invalid:
        out = out.replace(i,'_')
    return out


@register.filter(name='durationFormat')
def durationFormat(inp):
    return "%.1f" % (float(inp)/3600)

# from:
#    http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
#
@register.filter(name="call")
def callMethod(obj, methodName):
    method = getattr(obj, methodName)

    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

@register.filter(name="args")
def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []

    obj.__callArg += [arg]
    return obj

