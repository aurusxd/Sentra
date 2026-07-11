from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import create_app

app = create_app()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://sentra.fun",
        "https://www.sentra.fun",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
