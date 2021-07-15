from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Convert html to pdf to be called in pdf report views
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)    # pdf won't crash on special characters such as Latin or Chinese
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
