from django import template

register = template.Library()
@register.simple_tag
def multiply(num1, num2):
    return num1 * num2