import sys
import asyncio
import uvicorn
from dotenv import load_dotenv

def win_proactor_loop_factory():
    """Factory to explicitly instantiate ProactorEventLoop for current thread context."""
    return asyncio.ProactorEventLoop()

if __name__ == "__main__":
    load_dotenv()

    kwargs = {
        "app": "src.main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True
    }

    # Если мы на Windows, передаем саму функцию-фабрику создания цикла событий
    if sys.platform == "win32":
        kwargs["loop"] = win_proactor_loop_factory

    uvicorn.run(**kwargs)
