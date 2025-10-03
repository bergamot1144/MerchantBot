"""
Менеджер для создания клавиатур
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from constants import Buttons, CallbackData

class KeyboardManager:
    """Менеджер для создания клавиатур"""
    
    @staticmethod
    def get_merchant_main_menu() -> ReplyKeyboardMarkup:
        """Главное меню мерчанта"""
        keyboard = [
            [KeyboardButton(Buttons.PROFILE), KeyboardButton(Buttons.INFO)],
            [KeyboardButton(Buttons.CREATE_INVOICE), KeyboardButton(Buttons.CREATE_PAYOUT)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_profile_menu() -> ReplyKeyboardMarkup:
        """Меню профиля"""
        keyboard = [
            [KeyboardButton(Buttons.LOGOUT), KeyboardButton(Buttons.MAIN_MENU)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_admin_main_menu() -> ReplyKeyboardMarkup:
        """Главное меню админа"""
        keyboard = [
            [KeyboardButton(Buttons.USERS), KeyboardButton(Buttons.BROADCAST)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_admin_users_menu() -> ReplyKeyboardMarkup:
        """Меню управления пользователями"""
        keyboard = [
            [KeyboardButton(Buttons.ADD_USER), KeyboardButton(Buttons.DELETE_USER)],
            [KeyboardButton(Buttons.MAIN_MENU)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_main_menu_button() -> ReplyKeyboardMarkup:
        """Кнопка возврата в главное меню"""
        keyboard = [[KeyboardButton(Buttons.MAIN_MENU)]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_invoice_method_selection() -> InlineKeyboardMarkup:
        """Выбор метода инвойса"""
        keyboard = [
            [
                InlineKeyboardButton(Buttons.INVOICE_CARD, callback_data=CallbackData.INVOICE_METHOD_CARD),
                InlineKeyboardButton(Buttons.INVOICE_ONECLICK, callback_data=CallbackData.INVOICE_METHOD_ONECLICK),
                InlineKeyboardButton(Buttons.INVOICE_IBAN, callback_data=CallbackData.INVOICE_METHOD_IBAN)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payout_method_selection() -> InlineKeyboardMarkup:
        """Выбор метода выплаты"""
        keyboard = [
            [
                InlineKeyboardButton(Buttons.PAYOUT_CARD, callback_data=CallbackData.PAYOUT_METHOD_CARD),
                InlineKeyboardButton(Buttons.PAYOUT_IBAN, callback_data=CallbackData.PAYOUT_METHOD_IBAN)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_purpose_selection() -> InlineKeyboardMarkup:
        """Выбор назначения платежа"""
        keyboard = [
            [InlineKeyboardButton(Buttons.PURPOSE_POPOVNENNYA, callback_data=CallbackData.PAYOUT_PURPOSE_POPOVNENNYA)],
            [InlineKeyboardButton(Buttons.PURPOSE_POVORENNYA, callback_data=CallbackData.PAYOUT_PURPOSE_POVORENNYA)],
            [InlineKeyboardButton(Buttons.PURPOSE_PEREKAZ, callback_data=CallbackData.PAYOUT_PURPOSE_PEREKAZ)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_confirmation_buttons() -> InlineKeyboardMarkup:
        """Кнопки подтверждения"""
        keyboard = [
            [
                InlineKeyboardButton(Buttons.CONFIRM, callback_data="confirm"),
                InlineKeyboardButton(Buttons.CANCEL, callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_invoice_confirmation_buttons() -> InlineKeyboardMarkup:
        """Кнопки подтверждения инвойса"""
        keyboard = [
            [
                InlineKeyboardButton(Buttons.CONFIRM, callback_data=CallbackData.INVOICE_CONFIRM),
                InlineKeyboardButton(Buttons.CANCEL, callback_data=CallbackData.INVOICE_CANCEL)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payout_confirmation_buttons() -> InlineKeyboardMarkup:
        """Кнопки подтверждения выплаты"""
        keyboard = [
            [
                InlineKeyboardButton(Buttons.CONFIRM, callback_data=CallbackData.PAYOUT_CONFIRM),
                InlineKeyboardButton(Buttons.CANCEL, callback_data=CallbackData.PAYOUT_CANCEL)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_logout_cancel_button() -> InlineKeyboardMarkup:
        """Кнопка отмены выхода"""
        keyboard = [
            [InlineKeyboardButton(Buttons.CANCEL, callback_data=CallbackData.LOGOUT_CANCEL)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_skip_button() -> InlineKeyboardMarkup:
        """Кнопка пропуска"""
        keyboard = [
            [InlineKeyboardButton(Buttons.SKIP, callback_data=CallbackData.ADMIN_SKIP)]
        ]
        return InlineKeyboardMarkup(keyboard)
