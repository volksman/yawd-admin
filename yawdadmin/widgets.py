from itertools import chain
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class ContentTypeSelect(forms.Select):
    def __init__(self, object_id,  attrs=None, choices=()):
        self.object_id = 'id_%s' % object_id
        super(ContentTypeSelect, self).__init__(attrs, choices)
  
    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)

        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)

        for ctype in ContentType.objects.filter(pk__in=[int(c[0])for c in chain(self.choices, choices) if c[0]]):
            choiceoutput += '    \'%s\' : \'../../../%s/%s?t=%s\','  % ( str(ctype.pk), 
                    ctype.app_label, ctype.model, ctype.model_class()._meta.pk.name)

        choiceoutput += '};'

        output += ('<script>'
                   '(function($) {'
                   '  $(document).ready( function() {'
                   '%(choiceoutput)s'
                   '    $(\'#%(id)s\').change(function (){'
                   '        $(\'#%(fk_id)s\').val(\'\');'
                   '        $(\'#lookup_%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]+"&pop=1").siblings(\'strong\').html(\'\');'
                   '    });'
                   '  });'
                   '})(yawdadmin.jQuery);'
                   '</script>' % { 'choiceoutput' : choiceoutput, 
                                    'id' : attrs['id'],
                                    'fk_id' : self.object_id
                                  })
        return mark_safe(u''.join(output))


class AutoCompleteTextInput(forms.TextInput):

    def __init__(self, *args, **kwargs):
        if 'source' in kwargs:
            self.source = kwargs['source']
            del kwargs['source']
        else:
            self.source = None
        super(AutoCompleteTextInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if self.source:
            attrs['autocomplete'] = 'off'
        output = super(AutoCompleteTextInput, self).render(name, value, attrs)
        if self.source:
            js = '<script>(function($){$("#%(id)s").typeahead({source: function(query, process) { $.get("%(source)s", {query: query},function(data) { return typeof data.results == "undefined" ? false : process(data.results); }, "json") }});})(yawdadmin.jQuery);</script>' % {'id': attrs['id'], 'source': self.source}
        return output + mark_safe(js)

class BootstrapRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % unicode(w).replace('<label ', '<label class="radio inline" ') for w in self])+'&#xa0;')
