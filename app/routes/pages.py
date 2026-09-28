from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import COOKIE_NAME, get_user_id_from_token
from ..config import settings
from ..database import SessionLocal
from ..models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ctx(request):
    user = None
    uid = get_user_id_from_token(request.cookies.get(COOKIE_NAME))

    if uid:
        with SessionLocal() as db:
            user = db.get(User, uid)

    return {
        "request": request,
        "user": user,
        "app_name": settings.app_name
    }


for path, template in [
    ("/", "index.html"),
    ("/login", "login.html"),
    ("/register", "register.html"),
    ("/dashboard", "dashboard.html"),
    ("/planner/home", "home_planner.html"),
    ("/planner/party", "party_planner.html"),
    ("/planner/jewelry", "jewelry_planner.html"),
    ("/recommendations", "recommendations.html"),
    ("/history", "history.html"),
]:

    def make_view(t):
        async def view(request: Request):
            return templates.TemplateResponse(
                request=request,
                name=t,
                context=ctx(request)
            )

        return view

    router.add_api_route(
        path,
        make_view(template),
        methods=["GET"],
        response_class=HTMLResponse,
        name=template.replace(".html", "")
    )