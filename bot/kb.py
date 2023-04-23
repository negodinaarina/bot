from aiogram.types import KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_kb_full = InlineKeyboardMarkup(row_width=2)

inline_btn_true = InlineKeyboardButton('Правда', callback_data='pressed_true')
inline_btn_false = InlineKeyboardButton('Ложь', callback_data='pressed_false')

inline_kb_full.add(inline_btn_true, inline_btn_false)