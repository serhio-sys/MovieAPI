import os
from admin.database import AdminDB
from fastapi import APIRouter, Cookie, Body
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from admin.utils import serializer_dict
from .decorators import authentication_required
from database.database import b64crypt_decode


# Password must be encoded by module database.serializers function b64crypt_encode
ADMIN_PASSWORD = "YWRtaW4="
BASE_DIR = os.path.dirname(__file__)
admin_router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def get_base_context(request: Request, table_name: str = "") -> dict:
    return {"table_name": table_name, "request": request,
            "routes": [route for route in admin_router.routes if list(route.methods)[0] == "GET"
                       and "_table_update" not in route.name]}


@authentication_required()
@admin_router.get("/", name="admin_home")
def routes(request: Request):
    context = get_base_context(request=request)
    return templates.TemplateResponse("home.html", context=context)


@admin_router.get("/login/", name="admin_login")
def login_admin(request: Request, authenticated=Cookie(default=False)):
    if bool(authenticated):
        return RedirectResponse(url=request.url_for("admin_home"), status_code=303)
    return templates.TemplateResponse("auth.html", {"request": request})


@authentication_required()
@admin_router.get("/logout/", name="admin_logout")
def logout(request: Request):
    response = RedirectResponse(url=request.url_for("admin_login"), status_code=303)
    response.delete_cookie("authenticated")
    return response


@admin_router.post("/login/")
def login_post(request: Request, data=Body()):
    try:
        if data['admin_password'] == b64crypt_decode(ADMIN_PASSWORD):
            response = RedirectResponse(url=request.url_for("admin_home"), status_code=303)
            response.set_cookie("authenticated", "True")
            return response
    except KeyError:
        pass
    return ""


class AdminView:
    def __init__(self, table_name) -> None:
        self.table_name = table_name
        try:
            self.serializer_class = serializer_dict[table_name]
        except KeyError:
            del self
            return
        self.admin_query = AdminDB(table_name=table_name)
        self.generate_routes()

    def generate_routes(self):
        serializer_class = self.serializer_class

        @admin_router.get(f"/{self.table_name}/", name=self.table_name + "_table", response_class=HTMLResponse)
        @authentication_required()
        def list_route(request: Request, **kwargs):
            objects = self.serializer_class.auto_create_list(self.serializer_class,
                                                             self.admin_query.get_list_of_objects(kwargs['page']))
            context = get_base_context(request, self.table_name)
            context.update({
                "objects": objects,
                "attrs": [(name, var_type) for name, var_type in zip(self.serializer_class.__annotations__.keys(),
                                                                     self.serializer_class.__annotations__.values())]})
            return templates.TemplateResponse("model.html", context=context)

        @authentication_required()
        @admin_router.get(path=f"/{self.table_name}/" + "{pk}/",
                          name=self.table_name + "_table_update",
                          response_class=HTMLResponse)
        def route_update(request: Request, pk: int | str = 1):
            object_ = self.serializer_class.get_object(serializer_class, self.table_name, pk)

            context = get_base_context(request, self.table_name)
            context.update({
                "object": object_,
                "attrs": [(name, var_type) for name, var_type in zip(self.serializer_class.__annotations__.keys(),
                                                                     self.serializer_class.__annotations__.values())]
            })

            return templates.TemplateResponse("update.html", context=context)

        @authentication_required()
        @admin_router.patch(path=f"/{self.table_name}/" + "{pk}/")
        def route_update(request: Request, serializer: serializer_class, pk: int | str = 1):
            self.serializer_class.update_model(serializer, self.table_name, pk)
            return RedirectResponse(url=request.url_for(self.table_name+"_table_update", pk=pk), status_code=303)

        @authentication_required()
        @admin_router.post(f"/{self.table_name}/", name=self.table_name + "_table_post")
        def route_create(data: serializer_class):
            self.serializer_class.save_to_db(data, self.table_name)
            return ""

        @authentication_required()
        @admin_router.delete(f"/{self.table_name}/" + "{pk}/", name=self.table_name + "_table_delete")
        def route_delete(pk: int | str):
            self.serializer_class.delete_from_db(pk, self.table_name)
            return ""
