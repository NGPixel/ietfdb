from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

from ietf.ietfauth.utils import passes_test_decorator

from ietf.nomcom.utils import get_nomcom_by_year


def nomcom_private_key_required(view_func):
    def inner(request, *args, **kwargs):
        year = kwargs.get('year', None)
        if not year:
            raise Exception, 'View decorated with nomcom_private_key_required must receive a year argument'
        if not 'NOMCOM_PRIVATE_KEY_%s' % year in request.session:
            return HttpResponseRedirect('%s?back_to=%s' % (reverse('nomcom_private_key', None, args=(year, )), urlquote(request.get_full_path())))
        else:
            return view_func(request, *args, **kwargs)
    return inner
