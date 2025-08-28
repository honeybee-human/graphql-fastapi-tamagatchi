# GraphQL FastAPI Tamagotchi Game

A multiplayer Tamagotchi game built with FastAPI, GraphQL, and Vue.js. Players can create virtual pets, interact with them, and see other players' pets in real-time.

## Project Structure

- `app/` - Backend FastAPI application with GraphQL API
- `frontend/` - Vue.js frontend application
- `main.py` - Main entry point for the backend server
- `requirements.txt` - Python dependencies

## Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Git

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd graphql-fastapi-tamagatchi
```

### 2. Backend Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

## Running the Application

### Development Mode

#### 1. Start the Backend Server

From the project root directory:

```bash
python main.py
```

The backend server will start at http://localhost:8000

#### 2. Start the Frontend Development Server

In a new terminal, navigate to the frontend directory and run:

```bash
cd frontend
npm run serve
```

The frontend development server will start at http://localhost:8080

### Production Mode

1. Build the frontend:

```bash
cd frontend
npm run build
```

2. Run the backend server which will serve the built frontend:

```bash
python main.py
```

The application will be available at http://localhost:8000

## API Endpoints

- GraphQL API: http://localhost:8000/graphql
- WebSocket: ws://localhost:8000/ws/{user_id}

## Features

- User authentication (register/login)
- Create and manage virtual pets (Tamagotchis)
- Real-time interactions with pets (feed, play, sleep)
- Real-time mouse position tracking
- View other online users and their pets

## Game Mechanics

- Tamagotchis have stats (happiness, hunger, energy, health)
- Stats decrease over time
- Perform actions to increase stats
- Tamagotchis can die if not properly cared for
