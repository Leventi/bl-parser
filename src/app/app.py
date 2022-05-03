from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from . import api
from .services.monopoly import MonopolyParser
from .database import Session
from .settings import LOGGER, settings

app = FastAPI(
    title='Parser',
    description='Микросервис Parser',
    version='0.0.5',
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.on_event('startup')
@repeat_every(seconds=settings.scheduler_period, logger=LOGGER, wait_first=True)
def run_scheduler():
    """ Функция парсинга списка естественных монополий с сайта ФАС по расписанию """
    LOGGER.info("Start parsing -----------------------")
    session = Session()
    task = MonopolyParser(session)
    task.parser_monopoly()
    session.close()
    LOGGER.info("End parsing -------------------------")
