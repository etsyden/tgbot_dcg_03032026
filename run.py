import uvicorn
from multiprocessing import Process
import asyncio


def run_api():
    from app.api.main import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_bot():
    import os

    os.environ.setdefault("PYTHONPATH", ".")
    from app.main import main

    asyncio.run(main())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        run_api()
    elif len(sys.argv) > 1 and sys.argv[1] == "bot":
        run_bot()
    else:
        p1 = Process(target=run_api)
        p2 = Process(target=run_bot)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
