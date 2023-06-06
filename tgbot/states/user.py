from aiogram.fsm.state import StatesGroup, State


class UserSG(StatesGroup):
    main = State()
    subs = State()
    help = State()
    donate = State()


class SubscriptionSG(StatesGroup):
    service = State()
    months = State()
    reminder = State()
    check = State()
