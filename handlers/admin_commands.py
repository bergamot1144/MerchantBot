"""
Команды для администраторов
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseCommand


class ShowUsersCommand(BaseCommand):
    """Команда показа списка пользователей"""
    
    def __init__(self, bot_instance):
        super().__init__("👤 Пользователи")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(update.message.text):
            return False
        
        users = self.bot_instance.get_all_users()
        if users:
            message = "👤 Пользователи, у которых есть доступ к Боту:\n\n"
            for i, user in enumerate(users, 1):
                user_id, username_db, first_name, last_name, is_merchant, shop_id, shop_api_key, order_id_tag, created_at = user
                if is_merchant:
                    message += f"{i}) @{username_db}\n"
                    message += f"shop_id: {shop_id or 'Не указан'}\n"
                    message += f"shop_api_key: {shop_api_key or 'Не указан'}\n"
                    if order_id_tag:
                        message += f"order_id_tag: {order_id_tag}\n"
                    message += "\n"
        else:
            message = "👤 Пользователи, у которых есть доступ к Боту:\n\nСписок пуст."
        
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True


class CreateBroadcastCommand(BaseCommand):
    """Команда создания рассылки"""
    
    def __init__(self, bot_instance):
        super().__init__("✉️ Создать рассылку")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(update.message.text):
            return False
        
        message = "✉️ Создать рассылку\n\nОтправьте текст сообщения, которое хотите разослать всем пользователям Бота:"
        keyboard = [
            [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Устанавливаем состояние ожидания текста рассылки
        context.user_data['current_state'] = 'waiting_for_broadcast_text'
        return True


class AddUserCommand(BaseCommand):
    """Команда добавления пользователя"""
    
    def __init__(self, bot_instance):
        super().__init__("👤 Добавить пользователя")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(update.message.text):
            return False
        
        message = "👤 Добавить пользователя\n\nЧтобы открыть доступ к Боту, укажите @username аккаунта, который сможет создавать инвойсы и выплаты."
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Устанавливаем состояние ожидания username
        context.user_data['current_state'] = 'waiting_for_username'
        return True


class DeleteUserCommand(BaseCommand):
    """Команда удаления пользователя"""
    
    def __init__(self, bot_instance):
        super().__init__("❌ Удалить пользователя")
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(update.message.text):
            return False
        
        message = "Укажите @username аккаунта, который более не сможет взаимодействовать с Ботом."
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Устанавливаем состояние ожидания username для удаления
        context.user_data['current_state'] = 'waiting_for_delete_username'
        return True


class MainMenuCommand(BaseCommand):
    """Команда возврата в главное меню"""
    
    def __init__(self, bot_instance):
        super().__init__("👨🏻‍💻 Главное меню")
        self.bot_instance = bot_instance
    
    def can_handle(self, message_text: str) -> bool:
        return message_text in ["👨🏻‍💻 Главное меню", "◀️ Главное меню"]
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not self.can_handle(update.message.text):
            return False
        
        username = update.effective_user.username
        
        # Очищаем все состояния
        self._clear_all_states(context)
        
        if self.bot_instance.is_admin(username):
            # Админское меню
            keyboard = [
                [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        else:
            # Меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        return True
    
    def _clear_all_states(self, context: ContextTypes.DEFAULT_TYPE):
        """Очищает все состояния пользователя"""
        states_to_clear = [
            'current_state', 'waiting_for_username', 'waiting_for_shop_id', 
            'waiting_for_shop_api_key', 'waiting_for_order_id_tag', 'new_username', 
            'shop_id', 'shop_api_key', 'waiting_for_delete_username', 
            'waiting_for_delete_shop_id', 'delete_username', 'delete_user_shop_id',
            'waiting_for_logout_confirm', 'logout_username', 'waiting_for_broadcast_text'
        ]
        for state in states_to_clear:
            context.user_data.pop(state, None)
