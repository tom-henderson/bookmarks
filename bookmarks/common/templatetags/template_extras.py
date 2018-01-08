from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """
    Returns the URL of the current page, updating the
    get parameter 'field' with new value 'value'.

    Requires the RequestContext request instance to be
    provided to your template:
    http://stackoverflow.com/questions/2882490/get-the-current-url-within-a-django-template

    Example usage:
        {% url_replace request 'page' page_obj.next_page_number %}
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter
def render_markdown(text):
    try:
        import markdown
    except:
        return text

    return mark_safe(markdown.markdown(text, safe_mode='escape'))
