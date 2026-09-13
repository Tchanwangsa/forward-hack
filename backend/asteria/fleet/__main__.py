"""`python -m asteria.fleet` — the fleet service, on its own port."""

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "asteria.fleet.api:app",
        host=os.getenv("FLEET_HOST", "127.0.0.1"),
        port=int(os.getenv("FLEET_PORT", "8100")),
        reload=bool(os.getenv("FLEET_RELOAD")),
    )
