"""
Команды для мерчантов
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from handlers.base import BaseCommand
from states import UserState


class ProfileCommand(BaseCommand):
    """Команда показа профиля мерчанта"""
    
    def __init__(self, bot_instance):
        super().__init__("👤 Профиль")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        user_id = update.effective_user.id
        
        if not self.can_handle(update.message.text):
            return False
        
        # Проверяем, является ли пользователь мерчантом
        if not self.bot_instance.is_merchant(user_id):
            return False
        
        # Получаем данные мерчанта
        merchant_data = self.bot_instance.get_merchant_settings(user_id)
        
        if merchant_data:
            shop_id, shop_api_key, order_id_tag = merchant_data[1], merchant_data[2], merchant_data[3]
            message = f"👤 Профиль\n\n• Username: @{username}\n• Shop ID: {shop_id or 'Не указан'}\n• Shop API Key: {shop_api_key or 'Не указан'}\n• Order ID Tag: {order_id_tag or 'Не указан'}"
        else:
            message = f"👤 Профиль\n\n• Username: @{username}\n\nДанные мерчанта не найдены."
        
        keyboard = [
            [KeyboardButton("❌ Выйти из аккаунта"), KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True


class InfoCommand(BaseCommand):
    """Команда показа информационного блока"""
    
    def __init__(self, bot_instance):
        super().__init__("📄 Информация")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user_id = update.effective_user.id
        
        if not self.can_handle(update.message.text):
            return False
        
        # Проверяем, является ли пользователь мерчантом
        if not self.bot_instance.is_merchant(user_id):
            return False
        
        info_content = self.bot_instance.get_info_content()
        message = f"📄 Информация\n\n{info_content}"
        await update.message.reply_text(message)
        return True


class CreateInvoiceCommand(BaseCommand):
    """Команда создания инвойса"""
    
    def __init__(self, bot_instance):
        super().__init__("🎰 Создать инвойс")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user_id = update.effective_user.id
        
        if not self.can_handle(update.message.text):
            return False
        
        # Проверяем, является ли пользователь мерчантом
        if not self.bot_instance.is_merchant(user_id):
            return False
        
        message = "🎰 Выберите метод для инвойса"
        # Inline кнопки для выбора метода
        inline_keyboard = [
            [InlineKeyboardButton("💳 Card", callback_data="invoice_method_card"),
             InlineKeyboardButton("⚡ OneClick", callback_data="invoice_method_oneclick"),
             InlineKeyboardButton("🏦 IBAN", callback_data="invoice_method_iban")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        # KeyboardButton для главного меню
        keyboard = [
            [KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Отправляем сообщение с inline кнопками
        await update.message.reply_text(message, reply_markup=inline_markup)
        # Устанавливаем KeyboardButton без дополнительного текста
        await update.message.reply_text(".", reply_markup=reply_markup)
        return True


class CreatePayoutCommand(BaseCommand):
    """Команда создания выплаты"""
    
    def __init__(self, bot_instance):
        super().__init__("💎 Создать выплату")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user_id = update.effective_user.id
        
        if not self.can_handle(update.message.text):
            return False
        
        # Проверяем, является ли пользователь мерчантом
        if not self.bot_instance.is_merchant(user_id):
            return False
        
        message = "💎 Выберите метод для выплаты"
        # Inline кнопки для выбора метода
        inline_keyboard = [
            [InlineKeyboardButton("💳 Card", callback_data="payout_method_card"),
             InlineKeyboardButton("🏦 IBAN", callback_data="payout_method_iban")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        # KeyboardButton для главного меню
        keyboard = [
            [KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Отправляем сообщение с inline кнопками
        await update.message.reply_text(message, reply_markup=inline_markup)
        # Устанавливаем KeyboardButton без дополнительного текста
        await update.message.reply_text(".", reply_markup=reply_markup)
        return True


class LogoutCommand(BaseCommand):
    """Команда выхода из аккаунта"""
    
    def __init__(self, bot_instance):
        super().__init__("❌ Выйти из аккаунта")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        user_id = update.effective_user.id
        
        if not self.can_handle(update.message.text):
            return False
        
        # Проверяем, является ли пользователь мерчантом
        if not self.bot_instance.is_merchant(user_id):
            return False
        
        # Начинаем процесс выхода из аккаунта
        message = f"❌ Вы действительно хотите отвязать свой аккаунт от Бота?\n\nЧтобы подтвердить действие, отправьте свой @username в следующем сообщении."
        keyboard = [
            [InlineKeyboardButton("Отмена", callback_data="logout_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Убираем меню (ReplyKeyboardRemove)
        remove_keyboard = ReplyKeyboardRemove()
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        context.user_data['current_state'] = UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value
        context.user_data['logout_username'] = username
        return True
