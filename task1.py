import asyncio
import sentry_sdk
from sentry_sdk import Hub, capture_message
from sentry_sdk.integrations.asyncio import AsyncioIntegration

SENTRY_DSN="https://095875278cb642c0860527ed126333a9@o447951.ingest.sentry.io/6618415"

#
# Data is sent to this Sentry project:
# https://sentry.io/organizations/sentry-sdks/performance/summary/?project=6618415&query=http.method%3AGET&statsPeriod=24h&transaction=%2F&unselectedSeries=p100%28%29
#

#
# RESULT:
# https://sentry.io/organizations/sentry-sdks/performance/fastapi:e12d5795aba4414ebe6adc2457a55a99/?project=6618415&query=&showTransactions=recent&statsPeriod=24h&transaction=task1&unselectedSeries=p100%28%29
#

async def foo():
    #with sentry_sdk.start_span(op="foo"):
    await asyncio.sleep(0.5)

async def bar():
    #with sentry_sdk.start_span(op="bar"):
    await asyncio.sleep(0.5)

async def root():
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        integrations=[
            AsyncioIntegration(),
        ]
    )

    with sentry_sdk.start_transaction(name="task1"):
        with sentry_sdk.start_span(op="root"):
            await asyncio.gather(foo(), bar(), return_exceptions=True)

        sentry_sdk.flush()

if __name__ == "__main__":
    asyncio.run(root()) 