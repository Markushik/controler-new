"""
The main file responsible for launching the bot
"""

import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram_dialog import setup_dialogs
from loguru import logger
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from tgbot.config import settings
from handlers import client
from tgbot.dialogs.create import dialog
from tgbot.handlers import errors
from tgbot.handlers.client import start
from tgbot.middlewares.database import DbSessionMiddleware


async def main() -> None:
    """
    The main function responsible for launching the bot
    :return:
    """
    logger.add("../debug.log", format="{time} {level} {message}", level="DEBUG")
    logger.info("LAUNCHING BOT")

    storage = RedisStorage.from_url(
        url=f"redis://{settings.REDIS_HOST}/{settings.REDIS_DB}",
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    postgres_url = URL.create(drivername="postgresql+asyncpg", host=settings.POSTGRES_HOST,
                              port=settings.POSTGRES_PORT, username=settings.POSTGRES_USERNAME,
                              password=settings.POSTGRES_PASSWORD, database=settings.POSTGRES_DATABASE)

    bot = Bot(token=settings.API_TOKEN, parse_mode="HTML")
    disp = Dispatcher(storage=storage)

    engine = create_async_engine(url=postgres_url, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    disp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    disp.callback_query.middleware(CallbackAnswerMiddleware())

    disp.include_router(errors.router)
    disp.include_router(client.router)

    setup_dialogs(disp)
    disp.include_router(dialog)

    try:
        await disp.start_polling(bot, allowed_updates=disp.resolve_used_update_types())
    finally:
        await disp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (SystemExit, KeyboardInterrupt, ConnectionRefusedError):
        logger.warning("SHUTDOWN BOT")
