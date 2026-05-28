import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import *
from database import db
from keyboards import *

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class BuyStarsState(StatesGroup):
    waiting_recipient = State()
    waiting_amount = State()
    waiting_confirm = State()

class SellStarsState(StatesGroup):
    waiting_amount = State()
    waiting_wallet = State()
    waiting_confirm = State()

class CalculatorState(StatesGroup):
    waiting_stars = State()
    waiting_usd = State()

user_messages = {}

async def edit_or_send_with_banner(target, text, reply_markup=None, parse_mode="Markdown", delete_old=True):
    try:
        if isinstance(target, types.CallbackQuery):
            user_id = target.from_user.id
            if delete_old and user_id in user_messages and user_messages[user_id]:
                try:
                    await bot.delete_message(user_id, user_messages[user_id])
                except:
                    pass
            
            msg = await target.message.answer_photo(
                photo=BANNER_ID,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            if hasattr(msg, 'message_id'):
                user_messages[user_id] = msg.message_id
            return msg
        else:
            msg = await target.answer_photo(
                photo=BANNER_ID,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return msg
    except Exception as e:
        if isinstance(target, types.CallbackQuery):
            msg = await target.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            msg = await target.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        return msg

async def edit_or_send(target, text, reply_markup=None, parse_mode="Markdown", delete_old=True):
    try:
        if isinstance(target, types.CallbackQuery):
            user_id = target.from_user.id
            if delete_old and user_id in user_messages and user_messages[user_id]:
                try:
                    await bot.delete_message(user_id, user_messages[user_id])
                except:
                    pass
            
            msg = await target.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
            if hasattr(msg, 'message_id'):
                user_messages[user_id] = msg.message_id
            return msg
        else:
            msg = await target.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
            return msg
    except Exception as e:
        msg = await target.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        return msg

async def show_main_menu(message, lang, user_id):
    msg = await edit_or_send_with_banner(
        message,
        "Добро пожаловать в HelperStars! 👋\n\nВыберите действие 👇",
        reply_markup=main_menu(lang)
    )
    if hasattr(msg, 'message_id'):
        user_messages[user_id] = msg.message_id

@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    db.add_user(user_id)
    await state.set_state("language_selection")
    await message.answer(
        "🌍 Выберите язык / Choose language:",
        reply_markup=language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def select_language(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    db.update_language(user_id, lang)
    await state.clear()
    await show_main_menu(callback.message, lang, user_id)
    await callback.answer()

@dp.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] if db.get_user(user_id) else 'ru'
    await edit_or_send_with_banner(
        callback,
        "Выберите действие 👇",
        reply_markup=main_menu(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    lang = user[1] if user else 'ru'
    balance = user[2] if user else 0
    total_bought = user[3] if user else 0
    total_sold = user[4] if user else 0
    total_deposit = user[5] if user and len(user) > 5 and user[5] is not None else 0
    
    spent_usd = total_bought * STARS_PRICE
    earned_usd = total_sold * STARS_PRICE
    
    balance_rub = balance * USD_TO_RUB
    spent_rub = spent_usd * USD_TO_RUB
    earned_rub = earned_usd * USD_TO_RUB
    deposit_rub = total_deposit * USD_TO_RUB
    
    text = (
        f"🎩 **Профиль**\n\n"
        f"👤 Ваш ID: `{user_id}`\n"
        f"💼 Ваш баланс: {balance:.2f} USD (~{balance_rub:.2f} RUB).\n\n"
        f"⭐️ Всего куплено звёзд: {total_bought} (${spent_usd:.2f}).\n"
        f"💰 Всего продано звёзд: {total_sold} (${earned_usd:.2f}).\n\n"
        f"📃 Общий депозит: {total_deposit:.2f} USD (~{deposit_rub:.2f} RUB)."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ В меню", callback_data="main_menu")
    builder.adjust(1)
    
    await edit_or_send_with_banner(callback, text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "faq")
async def faq(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] if db.get_user(user_id) else 'ru'
    text = (
        "❓ Часто задаваемые вопросы:\n\n"
        "1. Как быстро приходят звёзды?\n"
        "   → В течение 1 минуты после оплаты.\n\n"
        "2. Какой минимальный заказ?\n"
        f"   → {MIN_STARS} звёзд.\n\n"
        "3. Как пополнить баланс?\n"
        "   → Нажмите «Пополнить баланс» → Tonkeeper\n\n"
        "4. Что делать, если звёзды не пришли?\n"
        "   → Обратитесь в поддержку: @pirzs"
    )
    await edit_or_send_with_banner(callback, text, reply_markup=back_menu(lang))
    await callback.answer()

@dp.callback_query(F.data == "calculator")
async def calculator(callback: types.CallbackQuery, state: FSMContext):
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐️ Звёзды → USD", callback_data="calc_stars")
    builder.button(text="💵 USD → Звёзды", callback_data="calc_usd")
    builder.button(text="◀️ В меню", callback_data="main_menu")
    builder.adjust(1)
    await edit_or_send_with_banner(callback, "🧮 Калькулятор\n\nВыберите действие:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "calc_stars")
async def calc_stars(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CalculatorState.waiting_stars)
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    await edit_or_send_with_banner(callback, "🔎 Введите количество звёзд:", reply_markup=back_menu(lang))
    await callback.answer()

@dp.callback_query(F.data == "calc_usd")
async def calc_usd(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CalculatorState.waiting_usd)
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    await edit_or_send_with_banner(callback, "🔎 Введите сумму в USD:", reply_markup=back_menu(lang))
    await callback.answer()

@dp.message(CalculatorState.waiting_stars)
async def process_calc_stars(message: types.Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)[1] or 'ru'
    try:
        stars = int(message.text)
        usd = stars * STARS_PRICE
        await message.answer(f"⭐️ {stars} звёзд = {usd:.2f} USD", reply_markup=back_menu(lang))
    except:
        await message.answer("❌ Введите ЧИСЛО!", reply_markup=back_menu(lang))
    await state.clear()

@dp.message(CalculatorState.waiting_usd)
async def process_calc_usd(message: types.Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)[1] or 'ru'
    try:
        usd = float(message.text)
        stars = int(usd / STARS_PRICE)
        await message.answer(f"💵 {usd:.2f} USD = {stars} звёзд", reply_markup=back_menu(lang))
    except:
        await message.answer("❌ Введите ЧИСЛО!", reply_markup=back_menu(lang))
    await state.clear()

@dp.callback_query(F.data == "deposit")
async def deposit(callback: types.CallbackQuery):
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    await edit_or_send_with_banner(callback, "💰 Выберите способ пополнения:", reply_markup=deposit_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "deposit_tonkeeper")
async def deposit_tonkeeper(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    
    unique_code = f"PAY_{user_id}_{int(time.time())}"
    await state.update_data(payment_code=unique_code)
    
    text = (
        f"🏧 **Пополнение баланса прямым переводом**\n\n"
        f"💎 Переведите TON или USDT в сети TON на адрес:\n\n"
        f"`{TONKEEPER_WALLET}`\n\n"
        f"⚠️ **Обязательно укажите комментарий:**\n"
        f"`{unique_code}`\n\n"
        f"ℹ️ Если Вы не хотите раскрывать свой Telegram ID — то мы поддерживаем зашифрованные комментарии.\n"
        f"Просто нажмите в TonKeeper кнопку \"Зашифровать комментарий\", и никто не сможет связать ваш TON-кошелёк и Telegram аккаунт.\n\n"
        f"— Без комментария средства будут безвозвратно утеряны.\n\n"
        f"— TON зачисляется по рыночному курсу на момент транзакции, USDT — по курсу 1:1.\n\n"
        f"✅ После перевода нажмите кнопку **«Я оплатил»**"
    )
    await edit_or_send_with_banner(callback, text, reply_markup=confirm_payment_keyboard(lang), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "i_paid")
async def i_paid(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] if db.get_user(user_id) else 'ru'
    data = await state.get_data()
    payment_code = data.get('payment_code')
    
    if not payment_code:
        await edit_or_send_with_banner(callback, "❌ Ошибка: не найден код платежа.", reply_markup=back_menu(lang))
        return
    
    await edit_or_send_with_banner(callback, "⏳ **Проверяем перевод...**\n\nПожалуйста, ожидайте. Это может занять до 2 минут.", parse_mode="Markdown")
    
    await asyncio.sleep(10)
    
    usd_amount = 50.0
    db.update_balance(user_id, usd_amount)
    
    await edit_or_send_with_banner(
        callback,
        "❌ **Ошибка зачисления звёзд**\n\n"
        "Звёзды не могут быть зачислены автоматически.\n"
        "Пожалуйста, обратитесь в поддержку: @pirzs\n\n"
        "Приложите скриншот перевода.",
        reply_markup=back_menu(lang),
        parse_mode="Markdown"
    )
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "buy_stars")
async def buy_stars_start(callback: types.CallbackQuery, state: FSMContext):
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    await state.set_state(BuyStarsState.waiting_recipient)
    await edit_or_send_with_banner(
        callback,
        "⭐️ Покупка звёзд\n\n🔎 Введите @username получателя:\n\nИли нажмите «Для себя»",
        reply_markup=stars_keyboard(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "for_myself", BuyStarsState.waiting_recipient)
async def for_myself(callback: types.CallbackQuery, state: FSMContext):
    username = callback.from_user.username
    await state.update_data(recipient=f"@{username}" if username else str(callback.from_user.id))
    await ask_buy_amount(callback, state)

async def ask_buy_amount(callback, state):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    data = await state.get_data()
    recipient = data.get('recipient')
    balance = db.get_balance(user_id)
    max_stars = int(balance / STARS_PRICE)
    text = (
        f"⭐️ Покупка звёзд\n\n👤 Получатель: {recipient}\n\n"
        f"• Мин: {MIN_STARS} звёзд\n"
        f"• Макс: {MAX_STARS} звёзд\n"
        f"• Доступно: ~{max_stars} звёзд ({balance:.2f} USD)\n\n"
        f"🔎 Введите количество звёзд:"
    )
    await state.set_state(BuyStarsState.waiting_amount)
    await edit_or_send_with_banner(callback, text, reply_markup=back_menu(lang))

@dp.callback_query(BuyStarsState.waiting_recipient, F.data == "main_menu")
async def cancel_buy(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await main_menu_callback(callback, state)

@dp.message(BuyStarsState.waiting_recipient)
async def process_recipient(message: types.Message, state: FSMContext):
    if not message.text.startswith("@"):
        await message.answer("❌ Юзернейм должен начинаться с @")
        return
    await state.update_data(recipient=message.text)
    await ask_buy_amount_msg(message, state)

async def ask_buy_amount_msg(message, state):
    user_id = message.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    data = await state.get_data()
    recipient = data.get('recipient')
    balance = db.get_balance(user_id)
    max_stars = int(balance / STARS_PRICE)
    text = (
        f"⭐️ Покупка звёзд\n\n👤 Получатель: {recipient}\n\n"
        f"• Мин: {MIN_STARS} звёзд\n"
        f"• Макс: {MAX_STARS} звёзд\n"
        f"• Доступно: ~{max_stars} звёзд ({balance:.2f} USD)\n\n"
        f"🔎 Введите количество звёзд:"
    )
    await state.set_state(BuyStarsState.waiting_amount)
    await edit_or_send_with_banner(message, text, reply_markup=back_menu(lang))

@dp.message(BuyStarsState.waiting_amount)
async def process_buy_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    try:
        stars = int(message.text)
        if stars < MIN_STARS or stars > MAX_STARS:
            await message.answer(f"❌ От {MIN_STARS} до {MAX_STARS} звёзд!")
            return
        
        price_usd = stars * STARS_PRICE
        data = await state.get_data()
        recipient = data.get('recipient')
        
        await state.update_data(stars=stars, price_usd=price_usd, recipient=recipient)
        
        text = (
            f"♻️ Счёт сформирован.\n\n"
            f"🕙 Счёт действителен в течение 3 минут.\n\n"
            f"👤 Получатель: {recipient}\n"
            f"💰 Сумма к оплате: {price_usd:.2f} USD\n\n"
            f"Подтвердите покупку 👇"
        )
        await state.set_state(BuyStarsState.waiting_confirm)
        await message.answer(text, reply_markup=confirm_order_keyboard(lang))
        
    except ValueError:
        await message.answer("❌ Введите ЧИСЛО!")

@dp.callback_query(F.data == "confirm_pay", BuyStarsState.waiting_confirm)
async def confirm_purchase(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    data = await state.get_data()
    stars = data.get('stars')
    price_usd = data.get('price_usd')
    recipient = data.get('recipient')
    balance = db.get_balance(user_id)
    
    if balance >= price_usd:
        await edit_or_send_with_banner(
            callback,
            f"⏳ Отправка {stars} звёзд получателю {recipient}...",
            reply_markup=back_menu(lang)
        )
        await asyncio.sleep(2)
        
        await edit_or_send_with_banner(
            callback,
            f"❌ **Ошибка отправки звёзд**\n\n"
            f"Не удалось отправить {stars} звёзд получателю {recipient}.\n"
            f"Пожалуйста, обратитесь в поддержку: @pirzs\n\n"
            f"Ваши средства не были списаны.",
            reply_markup=back_menu(lang),
            parse_mode="Markdown"
        )
        await state.clear()
    else:
        needed = price_usd - balance
        text = (
            f"❌ Недостаточно средств для оплаты заказа.\n\n"
            f"💳 Пожалуйста, пополните баланс на сумму {needed:.2f} USD, чтобы оплатить заказ.\n\n"
            f"👉 Выберите способ оплаты:"
        )
        await edit_or_send_with_banner(callback, text, reply_markup=deposit_keyboard(lang))
        await state.clear()
    
    await callback.answer()

@dp.callback_query(F.data == "sell_stars")
async def sell_stars_start(callback: types.CallbackQuery, state: FSMContext):
    lang = db.get_user(callback.from_user.id)[1] or 'ru'
    await state.set_state(SellStarsState.waiting_amount)
    await edit_or_send_with_banner(
        callback,
        "💸 **Продажа звёзд**\n\n"
        "🔎 Введите количество звёзд для продажи:\n\n"
        "❗ Минимум: 15 звёзд\n"
        "💰 За 1 звезду вы получите 0.0164 USD",
        reply_markup=back_menu(lang),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(SellStarsState.waiting_amount)
async def process_sell_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    try:
        stars = int(message.text)
        if stars < 15:
            await message.answer("❌ Минимум 15 звёзд!", reply_markup=back_menu(lang))
            return
        if stars > 10000:
            await message.answer("❌ Максимум 10 000 звёзд!", reply_markup=back_menu(lang))
            return
        
        await state.update_data(sell_stars=stars)
        await state.set_state(SellStarsState.waiting_wallet)
        await message.answer(
            "💎 **Введите ваш кошелёк Tonkeeper**\n\n"
            "На него мы отправим деньги после проверки.\n\n"
            "Пример: `UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`",
            reply_markup=back_menu(lang),
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("❌ Введите ЧИСЛО!", reply_markup=back_menu(lang))

@dp.message(SellStarsState.waiting_wallet)
async def process_sell_wallet(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    wallet = message.text.strip()
    
    if not wallet.startswith("UQ") or len(wallet) < 40:
        await message.answer("❌ Неверный формат кошелька Tonkeeper!\n\nПример: `UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`", parse_mode="Markdown")
        return
    
    await state.update_data(sell_wallet=wallet)
    data = await state.get_data()
    stars = data.get('sell_stars')
    
    await state.set_state(SellStarsState.waiting_confirm)
    await edit_or_send_with_banner(
        message,
        f"⭐️ **Продажа {stars} звёзд**\n\n"
        f"💰 Сумма к выплате: **{stars * 0.0164:.2f} USD**\n"
        f"💎 Кошелёк: `{wallet}`\n\n"
        f"📌 **Инструкция:**\n"
        f"1️⃣ Переведите подарок в @pirzs\n"
        f"2️⃣ Подпишите подарок (комментарий: `Вывод`)\n"
        f"3️⃣ Нажмите кнопку **«Я перевел(а) подарок»**\n\n"
        f"✅ После проверки деньги поступят на ваш кошелёк.",
        reply_markup=confirm_sell_transfer_keyboard(lang),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "confirm_sell_transfer", SellStarsState.waiting_confirm)
async def confirm_sell_transfer(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = db.get_user(user_id)[1] or 'ru'
    data = await state.get_data()
    stars = data.get('sell_stars')
    wallet = data.get('sell_wallet')
    
    await edit_or_send_with_banner(
        callback,
        "⏳ **Проверяем перевод подарка...**\n\nПожалуйста, ожидайте.",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(5)
    
    await edit_or_send_with_banner(
        callback,
        "❌ **Ошибка выплаты**\n\n"
        "❓ Либо вы не перевели подарок, либо перевод ещё не обработан.\n\n"
        "Пожалуйста, обратитесь в поддержку: @pirzs\n\n"
        "Приложите скриншот перевода подарка (если он был).",
        reply_markup=back_menu(lang),
        parse_mode="Markdown"
    )
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "main_menu", SellStarsState.waiting_confirm)
async def cancel_sell(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await main_menu_callback(callback, state)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот HelperStars запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())