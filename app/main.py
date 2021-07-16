import logging

from fastapi import FastAPI, Request

from app.slackbot_webhook import app_handler, bot_name

from app.config import Settings

# logging.basicConfig(level=logging.DEBUG)

api = FastAPI()


def init_sentry():
    if Settings().SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        sentry_sdk.init(dsn=Settings().SENTRY_DSN)
        return SentryAsgiMiddleware(api)
    else:
        return api


app = init_sentry()


@app.post(f"/slack/{bot_name}-tableau")
async def endpoint(req: Request):
    print(req.body())
    return await app_handler.handle(req)


@app.post("/slack/events")
async def events(req: Request):
    return await app_handler.handle(req)


@app.on_event("startup")
async def run_scheduler():
    pass
