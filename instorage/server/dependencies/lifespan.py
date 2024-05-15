from contextlib import asynccontextmanager

from fastapi import FastAPI

from instorage.database.connect_to_db import connect_to_db
from instorage.database.database import sessionmanager
from instorage.jobs.job_manager import job_manager
from instorage.main.aiohttp_client import aiohttp_client
from instorage.server.dependencies.ai_models import init_completion_models
from instorage.server.dependencies.predefined_roles import init_predefined_roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


async def startup():
    aiohttp_client.start()
    connect_to_db()
    await job_manager.init()

    # init predefined roles
    await init_predefined_roles()

    # init completion models
    await init_completion_models()


async def shutdown():
    await sessionmanager.close()
    await aiohttp_client.stop()
    await job_manager.close()
