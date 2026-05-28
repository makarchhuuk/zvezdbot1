from aiogram.utils.keyboard import InlineKeyboardBuilder

def language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(2)
    return builder.as_markup()

def main_menu(lang="ru"):
    builder = InlineKeyboardBuilder()
    if lang == "ru":
        builder.button(text="⭐️ Купить звёзды", callback_data="buy_stars")
        builder.button(text="💸 Продать звёзды", callback_data="sell_stars")
        builder.button(text="👤 Профиль", callback_data="profile")
        builder.button(text="❓ F.A.Q.", callback_data="faq")
        builder.button(text="🧮 Калькулятор", callback_data="calculator")
        builder.button(text="💰 Пополнить баланс", callback_data="deposit")
    else:
        builder.button(text="⭐️ Buy Stars", callback_data="buy_stars")
        builder.button(text="💸 Sell Stars", callback_data="sell_stars")
        builder.button(text="👤 Profile", callback_data="profile")
        builder.button(text="❓ F.A.Q.", callback_data="faq")
        builder.button(text="🧮 Calculator", callback_data="calculator")
        builder.button(text="💰 Deposit", callback_data="deposit")
    builder.adjust(2)
    return builder.as_markup()

def back_menu(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ В меню" if lang == "ru" else "◀️ Back", callback_data="main_menu")
    return builder.as_markup()

def confirm_order_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить" if lang == "ru" else "✅ Confirm", callback_data="confirm_pay")
    builder.button(text="❌ Отменить" if lang == "ru" else "❌ Cancel", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def stars_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Для себя" if lang == "ru" else "👤 For myself", callback_data="for_myself")
    builder.button(text="◀️ В меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def deposit_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Tonkeeper", callback_data="deposit_tonkeeper")
    builder.button(text="◀️ В меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def confirm_payment_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я оплатил" if lang == "ru" else "✅ I paid", callback_data="i_paid")
    builder.button(text="◀️ Отмена", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def confirm_sell_transfer_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я перевел(а) подарок" if lang == "ru" else "✅ I sent the gift", callback_data="confirm_sell_transfer")
    builder.button(text="◀️ Отмена", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()