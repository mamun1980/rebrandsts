from django import template

register = template.Library()


@register.filter(name="replace")
def replace(value, args):
    ignore_symbols = [' ', '.', '/']
    if args == '-':
        value = value.replace('_', args)
    elif args == '_':
        value = value.replace('-', args)
    for item in ignore_symbols:
        if item in value:
            value = value.replace(item, args)
    return value
