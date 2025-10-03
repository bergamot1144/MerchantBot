"""
Обработчики состояний пользователей
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseState


class WaitingForBroadcastTextState(BaseState):
    """Состояние ожидания текста рассылки"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_broadcast_text')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        broadcast_text = update.message.text.strip()
        context.user_data['broadcast_text'] = broadcast_text
        
        # Отправляем рассылку
        users = self.bot_instance.get_all_active_users()
        success_count = 0
        
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=user_id, text=broadcast_text)
                success_count += 1
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
        
        # Возвращаем в главное меню
        keyboard = [
            [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        await update.message.reply_text(f"✅ Рассылка создана\n\nСообщение отправлено {success_count} пользователям.")
        
        # Очищаем состояние
        self.set_state(context, None)
        context.user_data.pop('broadcast_text', None)
        return True


class WaitingForUsernameState(BaseState):
    """Состояние ожидания username для добавления пользователя"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_username')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили username, запрашиваем shop_id
        new_username = update.message.text.strip().replace('@', '')
        context.user_data['new_username'] = new_username
        
        message = f"Укажите ID Магазина, с которого пользователь @{new_username} сможет создавать инвойсы и выплаты."
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        self.set_state(context, 'waiting_for_shop_id')
        return True


class WaitingForShopIdState(BaseState):
    """Состояние ожидания shop_id"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_shop_id')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили shop_id, запрашиваем shop_api_key
        shop_id = update.message.text.strip()
        context.user_data['shop_id'] = shop_id
        
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        message = f"✅ Shop ID сохранен: {shop_id}\n\nТеперь отправьте shop_api_key:"
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        self.set_state(context, 'waiting_for_shop_api_key')
        return True


class WaitingForShopApiKeyState(BaseState):
    """Состояние ожидания shop_api_key"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_shop_api_key')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили shop_api_key, запрашиваем order_id_tag
        shop_api_key = update.message.text.strip()
        context.user_data['shop_api_key'] = shop_api_key
        
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        message = f"✅ Shop API Key сохранен\n\nУкажите значение, которое будет привязано к этому Telegram-аккаунту, как ORDER ID TAG при создании инвойса или выплаты."
        
        # Inline кнопка для пропуска
        inline_keyboard = [
            [InlineKeyboardButton("Пропустить", callback_data="skip_order_id_tag")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        await update.message.reply_text(message, reply_markup=inline_markup)
        await update.message.reply_text(".", reply_markup=reply_markup)
        
        self.set_state(context, 'waiting_for_order_id_tag')
        return True


class WaitingForOrderIdTagState(BaseState):
    """Состояние ожидания order_id_tag"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_order_id_tag')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили order_id_tag, завершаем добавление пользователя
        order_id_tag = update.message.text.strip()
        if order_id_tag == '-':
            order_id_tag = None
        
        new_username = context.user_data.get('new_username')
        shop_id = context.user_data.get('shop_id')
        shop_api_key = context.user_data.get('shop_api_key')
        
        # Добавляем пользователя
        success = self.bot_instance.grant_merchant_access(new_username, shop_id, shop_api_key, order_id_tag)
        
        if success:
            message = f"✅ Пользователь успешно добавлен\n\n@{new_username} теперь имеет доступ к функционалу Бота."
        else:
            message = f"⚠️ Ошибка при добавлении пользователя @{new_username}."
        
        # Возвращаем в главное меню
        keyboard = [
            [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        await update.message.reply_text(message)
        
        # Очищаем состояние
        self.set_state(context, None)
        context.user_data.pop('new_username', None)
        context.user_data.pop('shop_id', None)
        context.user_data.pop('shop_api_key', None)
        return True


class WaitingForDeleteUsernameState(BaseState):
    """Состояние ожидания username для удаления пользователя"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_delete_username')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили username для удаления, запрашиваем shop_id для подтверждения
        delete_username = update.message.text.strip().replace('@', '')
        
        # Проверяем, существует ли пользователь
        user_data = self.bot_instance.get_user_by_username(delete_username)
        if not user_data:
            message = f"⚠️ Ошибка\n\nПользователь @{delete_username} не найден в базе данных."
            keyboard = [
                [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
                [KeyboardButton("👨🏻‍💻 Главное меню")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(message, reply_markup=reply_markup)
            self.set_state(context, None)
            return True
        
        # Сохраняем данные пользователя для проверки
        context.user_data['delete_username'] = delete_username
        context.user_data['delete_user_shop_id'] = user_data[5]  # shop_id из базы
        
        message = f"Для подтверждения действия отправьте shop_id, к которому был привязан пользователь @{delete_username}."
        keyboard = [
            [KeyboardButton("👨🏻‍💻 Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        self.set_state(context, 'waiting_for_delete_shop_id')
        return True


class WaitingForDeleteShopIdState(BaseState):
    """Состояние ожидания shop_id для подтверждения удаления"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_delete_shop_id')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        username = update.effective_user.username
        
        if not self.bot_instance.is_admin(username):
            return False
            
        if not self.can_handle(context.user_data):
            return False
        
        # Получили shop_id для подтверждения удаления
        entered_shop_id = update.message.text.strip()
        correct_shop_id = context.user_data.get('delete_user_shop_id')
        delete_username = context.user_data.get('delete_username')
        
        if entered_shop_id != correct_shop_id:
            # Неверный shop_id - ошибка, возвращаем в главное меню
            message = f"⚠️ Ошибка\n\nПодтвердить удаление пользователя не удалось. Указанный shop_id не привязан к заявленному username."
            
            # Возвращаем в главное меню
            keyboard = [
                [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
            await update.message.reply_text(message)
            
            # Очищаем состояние
            self.set_state(context, None)
            context.user_data.pop('delete_username', None)
            context.user_data.pop('delete_user_shop_id', None)
            return True
        
        # Верный shop_id - удаляем пользователя
        success = self.bot_instance.delete_user(delete_username)
        
        if success:
            await update.message.reply_text(f"❌ Пользователь успешно удален")
            
            # Показываем обновленный список пользователей
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
            
            # Возвращаем в меню управления пользователями
            keyboard = [
                [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
                [KeyboardButton("◀️ Главное меню")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            message = f"⚠️ Ошибка при удалении пользователя @{delete_username}."
            keyboard = [
                [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
            await update.message.reply_text(message)
        
        # Очищаем состояние
        self.set_state(context, None)
        context.user_data.pop('delete_username', None)
        context.user_data.pop('delete_user_shop_id', None)
        return True


class WaitingForLogoutConfirmState(BaseState):
    """Состояние ожидания подтверждения выхода"""
    
    def __init__(self, bot_instance):
        super().__init__('waiting_for_logout_confirm')
        self.bot_instance = bot_instance
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not self.can_handle(context.user_data):
            return False
        
        entered_username = update.message.text.strip().replace('@', '')
        expected_username = context.user_data.get('logout_username')
        
        if entered_username == expected_username:
            # Правильный username - выходим из аккаунта
            user_id = update.effective_user.id
            success = self.bot_instance.revoke_merchant_access(user_id)
            
            if success:
                message = f"✅ Вы успешно вышли из аккаунта\n\n@{expected_username} больше не имеет доступа к функционалу Бота."
            else:
                message = "⚠️ Ошибка при выходе из аккаунта."
            
            await update.message.reply_text(message)
            
            # Очищаем состояние
            self.set_state(context, None)
            context.user_data.pop('logout_username', None)
        else:
            # Неправильный username
            message = f"⚠️ Неверный username. Ожидался: @{expected_username}"
            await update.message.reply_text(message)
        
        return True
