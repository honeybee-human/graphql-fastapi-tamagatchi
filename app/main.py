from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from jose import JWTError, jwt

from .graphql import schema
from .services.storage import GameStorage
from .services.websocket import ConnectionManager
from .routes.websocket import setup_websocket_routes
from .config import SECRET_KEY, ALGORITHM

# Initialize services
storage = GameStorage()
manager = ConnectionManager()

# Set up dependency injection
storage.set_connection_manager(manager)

# Inject storage into GraphQL resolvers
import app.graphql.queries as queries_module
import app.graphql.mutations as mutations_module
queries_module.storage = storage
mutations_module.storage = storage

# Custom context getter for authentication
async def get_context(request: Request):
    context = {"request": request}
    
    # Extract JWT token from Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                context["user_id"] = user_id
                # Add user_id to request for easier access
                request.user_id = user_id
        except JWTError:
            pass  # Invalid token, continue without authentication
    
    return context

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await storage.start_background_tasks()
    yield
    # Shutdown (cleanup if needed)
    pass

# FastAPI app with lifespan
app = FastAPI(title="Multiplayer Tamagotchi Game API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint with custom context
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)
app.include_router(graphql_app, prefix="/graphql")

# Setup WebSocket routes
setup_websocket_routes(app, storage, manager)

import os
dist_root = os.path.join("frontend", "dist")
assets_dir = os.path.join(dist_root, "assets")

# Mount static only if built assets exist
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# SPA fallback routes: serve index if present, else 404
index_html = os.path.join(dist_root, "index.html")

@app.get("/")
async def serve_index_root():
    if os.path.isfile(index_html):
        return FileResponse(index_html)
    return Response(content="Frontend not built", status_code=404)

@app.get("/{full_path:path}")
async def serve_index(full_path: str):
    if os.path.isfile(index_html):
        return FileResponse(index_html)
    return Response(content="Frontend not built", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)