import asyncio
import sentry_sdk
from sentry_sdk import Hub, capture_message, start_span
from sentry_sdk.integrations.asyncio import AsyncioIntegration

SENTRY_DSN="https://095875278cb642c0860527ed126333a9@o447951.ingest.sentry.io/6618415"

#
# Data is sent to this Sentry project:
# https://sentry.io/organizations/sentry-sdks/performance/summary/?project=6618415&query=http.method%3AGET&statsPeriod=24h&transaction=%2F&unselectedSeries=p100%28%29
#


async def _batch_task(task, pool, span, index):
    print(f"Current hub: {Hub.current}")
    print(f"Current scope: {Hub.current.scope}")
    print(f"Current span: {Hub.current.scope.span}")
    with start_span(op="make_something", description=f'task-{index}') as spanx:
        print(f"Created span: {spanx}")
        async with pool:
            with span.start_child(op="batch", description=f'task-{index}'):
                await task


async def batch(items, size=10):
    with start_span(op="utils", description='batch') as span:
        span.set_data('size', size)
        span.set_data('number_of_coroutines', len(items))

        if len(items) == 0:
            return

        loop = asyncio.get_event_loop()

        pool = asyncio.Semaphore(value=size)

        tasks = [
            loop.create_task(
                _batch_task(coroutine_item, pool, span, index)
            ) for index, coroutine_item in enumerate(items)
        ]

        try:
            await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_EXCEPTION
            )
        finally:
            # loop over unfinished tasks canceling them.
            for task in tasks:
                task.cancel()
                try:
                    # To raise any exception it might have thrown
                    await task
                except asyncio.CancelledError:
                    pass


async def foo():
    print("foo")
    with start_span(op="foo-one", description='foo-one'):
        with start_span(op="foo-two", description='foo-two'):
            with start_span(op="foo-three", description='foo-three'):
                await asyncio.sleep(0.5)


async def bar():
    print("bar")
    with start_span(op="bar-one", description='bar-one'):
        with start_span(op="bar-two", description='bar-two'):
            with start_span(op="bar-three", description='bar-three'):
                await asyncio.sleep(0.5)


async def baz():
    print("baz")
    with start_span(op="baz-one", description='baz-one'):
        with start_span(op="baz-two", description='baz-two'):
            with start_span(op="baz-three", description='baz-three'):
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

    with sentry_sdk.start_transaction(name="task2"):
        await batch([foo(), bar(), baz()])
        sentry_sdk.flush()


if __name__ == "__main__":
    asyncio.run(root())                 