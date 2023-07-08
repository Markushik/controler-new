from datetime import date, datetime

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, DialogProtocol
from aiogram_dialog.widgets.kbd import Button

from application.tgbot.dialogs.format import I18N_FORMAT_KEY
from application.tgbot.states.user import SubscriptionSG, UserSG

router = Router()


@router.message(CommandStart(), StateFilter("*"))
async def command_start(message: Message, dialog_manager: DialogManager) -> None:
    session = dialog_manager.middleware_data["session"]
    user = await session.get_user(user_id=message.from_user.id)

    if user is None:
        await session.add_user(
            user_id=message.from_user.id, user_name=message.from_user.first_name,
            chat_id=message.chat.id, language=message.from_user.language_code, count_subs=0
        )
        await session.commit()

    await dialog_manager.start(UserSG.MAIN, mode=StartMode.RESET_STACK)


async def on_click_get_subs_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def on_click_back_to_main_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.MAIN, mode=StartMode.RESET_STACK)


async def on_click_get_settings_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.SETTINGS, mode=StartMode.RESET_STACK)


async def on_click_get_help_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.HELP, mode=StartMode.RESET_STACK)


async def on_click_get_delete_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(UserSG.DELETE, mode=StartMode.RESET_STACK)


async def get_subs_for_output(dialog_manager: DialogManager, **kwargs) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    session = dialog_manager.middleware_data["session"]
    services = await session.get_services(user_id=dialog_manager.event.from_user.id)

    subs = [f"<b>{count + 1}. {item.Service.title}</b> — {datetime.date(item.Service.reminder)}\n"
            for count, item in enumerate(services)]

    match subs:
        case []:
            return {"subs": l10n.format_value("Nothing-output")}
        case _:
            return {"subs": ''.join(subs)}


async def get_subs_for_delete(dialog_manager: DialogManager, **kwargs) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    session = dialog_manager.middleware_data["session"]
    services = await session.get_services(user_id=dialog_manager.event.from_user.id)

    subs = [(item.Service.service_id, item.Service.title, datetime.date(item.Service.reminder).isoformat())
            for item in services]

    match subs:
        case []:
            return {"message": l10n.format_value("Nothing-output"), "subs": subs}
        case _:
            return {"message": l10n.format_value("Set-for-delete"), "subs": subs}


async def on_click_sub_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager,
                                item_id: str) -> None:
    await dialog_manager.start(UserSG.CHECK_DELETE, mode=StartMode.RESET_STACK)
    print(int(item_id))
    dialog_manager.dialog_data["service_id"] = int(item_id)


async def on_click_sub_create(callback: CallbackQuery, dialog: DialogProtocol, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    session = dialog_manager.middleware_data["session"]
    request = await session.get_all_positions(user_id=dialog_manager.event.from_user.id)
    count = request.scalar()

    if count.count_subs >= 7:
        await callback.message.edit_text(l10n.format_value("Error-subs-limit"))
        await dialog_manager.done()
        await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(SubscriptionSG.SERVICE, mode=StartMode.RESET_STACK)


async def service_name_handler(message: Message, dialog: DialogProtocol, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    if len(message.text) <= 30:
        dialog_manager.dialog_data["service"] = message.text
        await dialog_manager.switch_to(SubscriptionSG.MONTHS)
    else:
        await message.answer(l10n.format_value("Error-len-limit"))


async def months_count_handler(message: Message, dialog: DialogProtocol, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    if message.text.isdigit() and int(message.text) in range(1, 12 + 1):
        dialog_manager.dialog_data["months"] = int(message.text)
        await dialog_manager.switch_to(SubscriptionSG.REMINDER)
    else:
        await message.answer(l10n.format_value("Error-char-limit"))


async def on_click_calendar_reminder(callback: CallbackQuery, button: Button, dialog_manager: DialogManager,
                                     selected_date: date) -> None:
    dialog_manager.dialog_data["reminder"] = selected_date.isoformat()
    await dialog_manager.switch_to(SubscriptionSG.CHECK)


async def on_click_button_confirm(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    session = dialog_manager.middleware_data["session"]

    await session.add_subscription(title=dialog_manager.dialog_data['service'],
                                   months=dialog_manager.dialog_data['months'],
                                   reminder=datetime.fromisoformat(dialog_manager.dialog_data['reminder']),
                                   service_by_user_id=callback.from_user.id)
    await session.increment_count(user_id=dialog_manager.event.from_user.id)
    await session.commit()

    await callback.message.edit_text(l10n.format_value("Approve-sub-add"))
    await dialog_manager.done()
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def on_click_button_reject(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    await callback.message.edit_text(l10n.format_value("Error-sub-add"))
    await dialog_manager.done()
    await dialog_manager.start(UserSG.SUBS, mode=StartMode.RESET_STACK)


async def get_input_service_data(dialog_manager: DialogManager, **kwargs) -> None:
    return {
        "service": dialog_manager.dialog_data.get("service"),
        "months": dialog_manager.dialog_data.get("months"),
        "reminder": dialog_manager.dialog_data.get("reminder")
    }


async def on_click_sub_delete(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    The on_click_sub_selected function is called when the user clicks on a service in the list of services.
    It starts a new dialog with the UserSG.CHECK_DELETE state group, and sets its mode to StartMode.RESET_STACK,
    which means that the current dialog stack will be cleared before starting this new one.

    :param callback: CallbackQuery: Get information about the user that triggered the callback
    :param button: Button: Get the button object that was clicked
    :param dialog_manager: DialogManager: Access the dialog manager
    """
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    session = dialog_manager.middleware_data["session"]
    await session.delete_subscription(service_id=dialog_manager.dialog_data['service_id'])
    await session.decrement_count(user_id=dialog_manager.event.from_user.id)
    await session.commit()

    await callback.message.edit_text(l10n.format_value("Approve-sub-delete"))
    await dialog_manager.done()
    await dialog_manager.start(UserSG.DELETE, mode=StartMode.RESET_STACK)


async def on_click_sub_not_delete(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    l10ns, lang = dialog_manager.middleware_data["l10ns"], dialog_manager.middleware_data["lang"]
    l10n = l10ns[lang]

    await callback.message.edit_text(l10n.format_value("Reject-sub-delete"))
    await dialog_manager.done()
    await dialog_manager.start(UserSG.DELETE, mode=StartMode.RESET_STACK)


async def on_click_change_lang(callback: CallbackQuery, button: Button, dialog_manager: DialogManager,
                               item_id: str) -> None:
    session = dialog_manager.middleware_data["session"]
    l10ns = dialog_manager.middleware_data["l10ns"]

    match item_id:
        case "0":
            await callback.answer("Вы сменили язык на 🇷🇺 Русский")
            lang = "ru"
            await session.update_language(user_id=dialog_manager.event.from_user.id, language="ru")
            await session.commit()
        case "1":
            await callback.answer("You switched language to 🇬🇧 English")
            lang = "en"
            await session.update_language(user_id=dialog_manager.event.from_user.id, language="en")
            await session.commit()

    l10n = l10ns[lang]
    dialog_manager.middleware_data[I18N_FORMAT_KEY] = l10n.format_value


async def get_langs_for_output(dialog_manager: DialogManager, **kwargs) -> None:
    return {"langs": [item for item in enumerate([" 🇷🇺 Русский", " 🇬🇧 English"])]}
