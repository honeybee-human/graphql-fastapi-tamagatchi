from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from jose import JWTError, jwt

from .graphql import schema
from .services.storage import GameStorage
from .services.websocket import ConnectionManager
from .routes.websocket import setup_websocket_routes
from .config import SECRET_KEY, ALGORITHM


storage = GameStorage()
manager = ConnectionManager()


storage.set_connection_manager(manager)


import app.graphql.queries as queries_module
import app.graphql.mutations as mutations_module
queries_module.storage = storage
mutations_module.storage = storage


async def get_context(request: Request):
    context = {"request": request}


    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                context["user_id"] = user_id

                request.user_id = user_id
        except JWTError:
            pass

    return context

@asynccontextmanager
async def lifespan(app: FastAPI):

    await storage.start_background_tasks()
    yield

    pass


app = FastAPI(title="Multiplayer Tamagotchi Game API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)
app.include_router(graphql_app, prefix="/graphql")


setup_websocket_routes(app, storage, manager)


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
