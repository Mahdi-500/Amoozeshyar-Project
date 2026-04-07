from django import template

register = template.Library()
@register.simple_tag(name="dict_value")
def get_exact_value_by_key(dict, key, inner_index,index):
    return dict[key][inner_index][index]