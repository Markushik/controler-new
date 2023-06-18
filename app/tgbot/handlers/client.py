from datetime import date, datetime

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, DialogProtocol
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Services, Users
from app.tgbot.middlewares.fluent import TranslatorRunnerMiddleware
from app.tgbot.states.user import SubscriptionSG, UserSG

router = Router()
router.message.middleware(TranslatorRunnerMiddleware())


async def get_data(dialog_manager: DialogManager, **kwargs) -> None:
    return {
        "service": f"<b>Сервис:</b> <code>{dialog_manager.dialog_data.get('service')}</code>\n",
        "months": f"<b>Длительность:</b> <code>{dialog_manager.dialog_data.get('months')} (мес.)</code>\n",
        "reminder": f"<b>Оповестить: </b> <code>{dialog_manager.dialog_data.get('reminder')}</code>"
    }


async def get_subs(dialog_manager: DialogManager, **kwargs) -> None:
    session: AsyncSession = dialog_manager.middleware_data["session"]
    request = await session.execute(
        select(Services)
        .where(Services.service_by_user_id == dialog_manager.event.from_user.id)
    )
    result_all = request.fetchall()

    match result_all:
        case []:
            return {"subs": "<b>🤷‍♂️ Кажется</b>, мы ничего <b>не нашли...</b>"}
        case _:
            subs = [f"<b>{count + 1}. {item.Services.title}</b> – {datetime.date(item.Services.reminder)}\n"
                    for count, item in enumerate(result_all)]
            return {"subs": ''.join(subs)}


@router.message(CommandStart(), StateFilter("*"))
async def command_start(message: Message, dialog_manager: DialogManager) -> None:
    # i18n: Any = dialog_manager.middleware_data["i18n"]
    # print(message.from_user.language_code)
    # await message.answer(i18n.hello())

    session: AsyncSession = dialog_manager.middleware_data["session"]
    await session.merge(
        Users(
            user_id=message.from_user.id,
            user_name=message.from_user.first_name,
            chat_id=message.chat.id,
            language=message.from_user.language_code,
            count_subs=0,
        )
    )
    await session.commit()

    await dialog_manager.start(UserSG.MAIN, mode=StartMode.RESET_STACK)


async def on_click_start_create_sub(query: CallbackQuery, dialog: DialogProtocol,
                                    dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data["session"]
    request = await session.execute(
        select(Users)
        .where(Users.user_id == dialog_manager.event.from_user.id)
    )
    result_all = request.one()

    if int(result_all.Users.count_subs) <= 7:
        await dialog_manager.start(SubscriptionSG.SERVICE, mode=StartMode.RESET_STACK)
    else:
        await query.message.edit_text("<b>🚫 Ошибка:</b> Достигнут лимит подписок")
        await dialog_manager.done()
        await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def service_name_handler(message: Message, dialog: DialogProtocol, dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data["service"] = message.text
    await dialog_manager.switch_to(SubscriptionSG.MONTHS)


async def months_count_handler(message: Message, dialog: DialogProtocol, dialog_manager: DialogManager) -> None:
    if message.text.isdigit() and int(message.text) in range(1, 12 + 1):
        dialog_manager.dialog_data["months"] = int(message.text)
        await dialog_manager.switch_to(SubscriptionSG.REMINDER)
    else:
        await message.answer(text="<b>🚫 Ошибка:</b> Недопустимые символы")


async def on_click_calendar_reminder(query: CallbackQuery, button: Button, dialog_manager: DialogManager,
                                     selected_date: date) -> None:
    dialog_manager.dialog_data["reminder"] = selected_date.isoformat()
    await dialog_manager.switch_to(SubscriptionSG.CHECK)
    await query.answer()


async def on_click_button_confirm(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    session: AsyncSession = dialog_manager.middleware_data["session"]
    await session.merge(
        Services(
            title=dialog_manager.dialog_data.get('service'),
            months=dialog_manager.dialog_data.get('months'),
            reminder=datetime.fromisoformat(dialog_manager.dialog_data.get('reminder')),
            service_by_user_id=query.from_user.id
        )
    )
    await session.merge(
        Users(
            user_id=query.from_user.id,
            count_subs=Users.count_subs + 1
        )
    )
    await session.commit()

    await query.message.edit_text("<b>✅ Одобрено:</b> Данные успешно записаны")
    await dialog_manager.done()
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def on_click_button_reject(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await query.message.edit_text("<b>❎ Отклонено:</b> Данные не записаны")
    await dialog_manager.done()
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def on_click_get_subs(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def on_click_back_to_main(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.MAIN, mode=StartMode.RESET_STACK)


async def on_click_get_settings(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.DONATE, mode=StartMode.RESET_STACK)


async def on_click_get_help(query: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.HELP, mode=StartMode.RESET_STACK)