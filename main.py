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
        hub = sentry_sdk.Hub.current
        print(f"~~~ 1 current span: {hub.scope.span}")        
        with hub.start_span(op="cache.save", description="in the request phase of CounterMiddleware") as middleware_span:
            print(f"~~~~~ 1 started span: {middleware_span}")
            print(f"~~~~~ 1 hub: {hub}")
            print(f"~~~~~ 1 scope: {hub.scope}")
            print(f"~~~~~ 1 new current span: {hub.scope.span}")
            time.sleep(0.02)

        async def count_hits(message):
            if message["type"] == "http.response.start":
                # this is the code that is call in the "response" phase of the middleware
                hub = sentry_sdk.Hub.current
                print(f"~~~ 2 current span: {hub.scope.span}")        
                with hub.start_span(op="cache.get_item", description="in the response phase of CounterMiddleware") as middleware_span:
                    print(f"~~~~~ 2 started span: {middleware_span}")
                    print(f"~~~~~ 2 hub: {hub}")
                    print(f"~~~~~ 2 scope: {hub.scope}")
                    print(f"~~~~~ 2 new current span: {hub.scope.span}")
                    time.sleep(0.03)

            await send(message)

        # calling next middleware in stack
        await self.app(scope, receive, count_hits)

app.add_middleware(CounterMiddleware)
