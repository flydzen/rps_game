import asyncio


def run_task(task):
    loop = asyncio.get_event_loop()
    loop.create_task(task)


User = str
