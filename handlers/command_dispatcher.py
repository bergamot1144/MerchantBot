"""
Диспетчер команд - основной класс для обработки всех входящих сообщений
"""
from typing import List
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler, BaseCommand, BaseState
from handlers.admin_commands import (
    ShowUsersCommand, CreateBroadcastCommand, AddUserCommand, 
    DeleteUserCommand, MainMenuCommand
)
from handlers.merchant_commands import (
    ProfileCommand, InfoCommand, CreateInvoiceCommand, 
    CreatePayoutCommand, LogoutCommand
)
from handlers.states import (
    WaitingForBroadcastTextState, WaitingForUsernameState, WaitingForShopIdState,
    WaitingForShopApiKeyState, WaitingForOrderIdTagState, WaitingForDeleteUsernameState,
    WaitingForDeleteShopIdState, WaitingForLogoutConfirmState
)


class CommandDispatcher:
    """Диспетчер команд для обработки всех входящих сообщений"""
    
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance
        self.commands: List[BaseCommand] = []
        self.states: List[BaseState] = []
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Инициализирует все обработчики команд и состояний"""
        
        # Команды администратора
        self.commands.extend([
            ShowUsersCommand(self.bot_instance),
            CreateBroadcastCommand(self.bot_instance),
            AddUserCommand(self.bot_instance),
            DeleteUserCommand(self.bot_instance),
        ])
        
        # Команды мерчанта
        self.commands.extend([
            ProfileCommand(self.bot_instance),
            InfoCommand(self.bot_instance),
            CreateInvoiceCommand(self.bot_instance),
            CreatePayoutCommand(self.bot_instance),
            LogoutCommand(self.bot_instance),
        ])
        
        # Общие команды (должны быть в конце)
        self.commands.append(MainMenuCommand(self.bot_instance))
        
        # Состояния
        self.states.extend([
            WaitingForBroadcastTextState(self.bot_instance),
            WaitingForUsernameState(self.bot_instance),
            WaitingForShopIdState(self.bot_instance),
            WaitingForShopApiKeyState(self.bot_instance),
            WaitingForOrderIdTagState(self.bot_instance),
            WaitingForDeleteUsernameState(self.bot_instance),
            WaitingForDeleteShopIdState(self.bot_instance),
            WaitingForLogoutConfirmState(self.bot_instance),
        ])
    
    async def dispatch_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Обрабатывает входящее сообщение, передавая его соответствующему обработчику
        
        Returns:
            bool: True если сообщение было обработано, False иначе
        """
        
        # Сначала проверяем состояния
        for state in self.states:
            if await state.handle(update, context):
                return True
        
        # Затем проверяем команды
        for command in self.commands:
            if await command.handle(update, context):
                return True
        
        return False
    
    def add_command(self, command: BaseCommand):
        """Добавляет новую команду"""
        self.commands.append(command)
    
    async def dispatch_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Обрабатывает входящий callback query
        
        Returns:
            bool: True если callback query был обработан, False иначе
        """
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        # Обработка кнопки "Пропустить" для order_id_tag
        if callback_data == "skip_order_id_tag":
            username = update.effective_user.username
            
            if not self.bot_instance.is_admin(username):
                return False
            
            # Завершаем добавление пользователя без order_id_tag
            new_username = context.user_data.get('new_username')
            shop_id = context.user_data.get('shop_id')
            shop_api_key = context.user_data.get('shop_api_key')
            
            # Добавляем пользователя
            success = self.bot_instance.grant_merchant_access(new_username, shop_id, shop_api_key, None)
            
            if success:
                message = f"✅ Пользователь успешно добавлен\n\n@{new_username} теперь имеет доступ к функционалу Бота."
            else:
                message = f"⚠️ Ошибка при добавлении пользователя @{new_username}."
            
            # Возвращаем в главное меню
            keyboard = [
                [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
            await query.message.reply_text(message)
            
            # Очищаем состояние
            context.user_data['current_state'] = None
            context.user_data.pop('new_username', None)
            context.user_data.pop('shop_id', None)
            context.user_data.pop('shop_api_key', None)
            return True
        
        # Обработка кнопки "Отмена" для выхода из аккаунта
        elif callback_data == "logout_cancel":
            user_id = update.effective_user.id
            
            if not self.bot_instance.is_merchant(user_id):
                return False
            
            # Возвращаем в главное меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
            await query.message.reply_text("❌ Выход из аккаунта отменен.")
            
            # Очищаем состояние
            context.user_data['current_state'] = None
            context.user_data.pop('logout_username', None)
            return True
        
        return False
