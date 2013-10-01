"""
Generally helpful utility functions.
"""


def _ask_for_it_by_name(name):
    "Returns an object referenced by absolute path."
    bits = name.split(".")

    ## what if there is no absolute reference?
    if len(bits)>1:
        modulename = ".".join(bits[:-1])
    else:
        modulename=bits[0]
        
    module = __import__(modulename, {}, {}, bits[-1])
    
    if len(bits) == 1:
        return module
    else:
        return getattr(module, bits[-1])


def ask_for_it_by_name(name): 
    "Returns an object referenced by absolute path. (Memoised outer wrapper)"
    if name not in ask_for_it_by_name.cache: 
        ask_for_it_by_name.cache[name] = _ask_for_it_by_name(name) 
    return ask_for_it_by_name.cache[name] 
ask_for_it_by_name.cache = {} 


def get_attribute(item, attribute):
    """
    Like getattr, but recursive (i.e. you can ask for 'foo.bar.yay'.)
    """
    value = item
    for part in attribute.split("."):
        value = getattr(value, part)
    return value

def auto_through(field):
    "Returns if the M2M class passed in has an autogenerated through table or not."
    return (
        # Django 1.0/1.1
        (not field.rel.through)
        or
        # Django 1.2+
        getattr(getattr(field.rel.through, "_meta", None), "auto_created", False)
    )

def auto_model(model):
    "Returns if the given model was automatically generated."
    return getattr(model._meta, "auto_created", False)

def memoize(function):
    "Standard memoization decorator."
    name = function.__name__
    _name = '_' + name
    
    def method(self):
        if not hasattr(self, _name):
            value = function(self)
            setattr(self, _name, value)
        return getattr(self, _name)
    
    def invalidate():
        if hasattr(method, _name):
            delattr(method, _name)
        
    method.__name__ = function.__name__
    method.__doc__ = function.__doc__
    method._invalidate = invalidate
    return method
