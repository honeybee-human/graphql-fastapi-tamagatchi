from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from .graphql import schema
from .services.storage import GameStorage
from .services.websocket import ConnectionManager
from .routes.websocket import setup_websocket_routes

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

# GraphQL endpoint
graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)
app.include_router(graphql_app, prefix="/graphql")

# Setup WebSocket routes
setup_websocket_routes(app, storage, manager)

# Serve static files (for Vue.js frontend)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)