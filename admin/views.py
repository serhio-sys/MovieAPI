import os
from admin.database import AdminDB
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from admin.utils import serializer_dict

admin_router = APIRouter()
BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR,"templates"))


def get_base_context(request: Request) -> dict:
    return {"request":request, "routes":[route for route in admin_router.routes if list(route.methods)[0] == "GET"]}

@admin_router.get("/")
def routes(request: Request):
    return templates.TemplateResponse("home.html",get_base_context(request=request))

class AdminView:
    def __init__(self,table_name) -> None:
        self.table_name = table_name
        try:    
            self.serializer_class = serializer_dict[table_name]
        except KeyError:
            del self
            return
        self.admin_query = AdminDB(table_name=table_name)
        self.generate_routes()

    def generate_routes(self):
        
        @admin_router.get(f"/{self.table_name}/",name=self.table_name+"_table", response_class=HTMLResponse)
        def list_route(request : Request, page : int = 1):
            objects = self.serializer_class.auto_create_list(self.serializer_class,self.admin_query.get_list_of_objects(page))
            context = get_base_context(request)
            context.update({
                "objects":objects,
                "attrs":[(name,var_type) for name, var_type in zip(self.serializer_class.__annotations__.keys(),
                                        self.serializer_class.__annotations__.values())]})
            return templates.TemplateResponse("model.html",context=context)
        
        @admin_router.post(f"/{self.table_name}/",name=self.table_name+"_table_post")
        def route_create(data : self.serializer_class):
            self.serializer_class.save_to_db(data,self.table_name)
            return ""
