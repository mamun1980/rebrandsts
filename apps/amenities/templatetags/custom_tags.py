from django import template

register = template.Library()


@register.filter(name="replace_hyphen_to_space")
def replace_hyphen_to_space(value):
    return value.replace("-", " ")


@register.filter
def get_model_name(value):
    name = str(value.__class__.__name__)
    return name
