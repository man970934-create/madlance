def payment_method_keyboard(payment_type: str = "") -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💎 CryptoBot (Криптовалюта)",
            callback_data=f"pay_crypto:{payment_type}"
        )],
        [InlineKeyboardButton(
            text="💳 ЮKassa (Банковская карта)",
            callback_data=f"pay_yookassa:{payment_type}"
        )],
        [InlineKeyboardButton(text="« Назад", callback_data="show_tariffs")]
    ])
