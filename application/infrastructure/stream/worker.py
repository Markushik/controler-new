import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from loguru import logger
from nats.js import JetStreamContext
from ormsgpack.ormsgpack import unpackb


async def nats_polling(bot: Bot, i18n_middleware, jetstream: JetStreamContext) -> None:
    subscribe = await jetstream.subscribe(subject='service_notify.message')

    async for message in subscribe.messages:
        try:
            data = unpackb(message.data)

            user_id = data["user_id"]
            service = data["service_name"]
            language = data["language"]

            l10ns = i18n_middleware.l10ns
            l10n = l10ns[language]

            await bot.send_message(
                chat_id=user_id,
                text=l10n.format_value("Notification-message", {"service": service})
            )
            await message.ack()
        except TelegramRetryAfter as ex:
            logger.info(f"LIMIT EXCEEDED, CONTINUE IN: {ex.retry_after}")
            await asyncio.sleep(float(ex.retry_after))
            continue
        except TelegramForbiddenError:
            await message.ack()
            continue
        except TimeoutError:
            pass
