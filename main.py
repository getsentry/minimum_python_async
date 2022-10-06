import time

from fastapi import FastAPI

import sentry_sdk

SENTRY_DSN="https://095875278cb642c0860527ed126333a9@o447951.ingest.sentry.io/6618415"

#
# Data is sent to this Sentry project:
# https://sentry.io/organizations/sentry-sdks/performance/summary/?project=6618415&query=http.method%3AGET&statsPeriod=24h&transaction=%2F&unselectedSeries=p100%28%29
#

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
    send_default_pii=True,
    debug=True,
)

app = FastAPI(debug=True)

@app.get("/")
async def home():
    return {"Hello": "Home World"}

class CounterMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # only handle http requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # this code is called in the "request" phase of the middleware
        path = scope.get("path")

        hub = sentry_sdk.Hub.current
        with hub.start_span(op="cache.save", description="in the request phase of CounterMiddleware") as middleware_span:
            print('so something here with request data')
            time.sleep(0.02)

        async def count_hits(message):
            if message["type"] == "http.response.start":
                # this is the code that is call in the "response" phase of the middleware
                hub = sentry_sdk.Hub.current
                with hub.start_span(op="cache.get_item", description="in the response phase of CounterMiddleware") as middleware_span:
                    print('so something here with response data')
                    time.sleep(0.04)

            await send(message)

        # calling next middleware in stack
        await self.app(scope, receive, count_hits)

app.add_middleware(CounterMiddleware)
