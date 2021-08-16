import logging

from fastapi import FastAPI, Request

from app.commons.slackbot_webhook import app_handler, bot_name
from app.controller.chromedriver import driver

from app.config import Settings

config = Settings()
if config.LOGGING_LEVEL == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

api = FastAPI()


def init_sentry(app):
    if config.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        sentry_sdk.init(dsn=config.SENTRY_DSN)
        app.add_middleware(SentryAsgiMiddleware)
    return app


app = init_sentry(api)


@app.post(f"/slack/{bot_name}-tableau")
async def tableau_endpoint(req: Request):
    return await app_handler.handle(req)


@app.post(f"/slack/{bot_name}-redash")
async def redash_endpoint(req: Request):
    return await app_handler.handle(req)


@app.post("/slack/events")
async def events(req: Request):
    return await app_handler.handle(req)


@app.get("/")
async def home(req: Request):
    return "Welcome"


@app.on_event("shutdown")
async def run_scheduler():
    logging.info("Stopping driver...")
    if driver:
        driver.quit()
