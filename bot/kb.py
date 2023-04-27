from aiogram.types import KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_kb_full = InlineKeyboardMarkup(row_width=2)

inline_btn_true = InlineKeyboardButton('Правда', callback_data='pressed_true')
inline_btn_false = InlineKeyboardButton('Ложь', callback_data='pressed_false')

inline_kb_full.add(inline_btn_true, inline_btn_false)

features_kb_full = InlineKeyboardMarkup(row_width=3)

feature1_btn = InlineKeyboardButton('1', callback_data='0')
feature2_btn = InlineKeyboardButton('2', callback_data='1')
feature3_btn = InlineKeyboardButton('3', callback_data='2')
features_kb_full.add(feature1_btn, feature2_btn, feature3_btn)