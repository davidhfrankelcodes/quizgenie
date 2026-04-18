import json
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
templates.env.filters["fromjson"] = json.loads


def render(request: Request, template_name: str, ctx: dict, current_user=None):
    ctx.update({"current_user": current_user})
    return templates.TemplateResponse(request, template_name, ctx)
