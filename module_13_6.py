from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = "7"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kbi = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kbi.add(button3, button4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kbi)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()
    formula_message = "Для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161."
    await call.message.answer(formula_message)


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите свой возраст(г):")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await message.answer("Введите свой рост(см):")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    growth = message.text
    await state.update_data(growth=growth)
    await message.answer("Введите свой вес(кг):")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def finish(message: types.Message, state: FSMContext):
    weight = message.text
    await state.update_data(weight=weight)
    data = await state.get_data()
    kcal = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161
    await message.answer(f"Женщине Вашего возраста, веса и роста необходимо потреблять "
                         f"{kcal} ккал в сутки")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
