"""
Обработчики сообщений для различных состояний
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from states import UserState, StateManager
from api_client import Konvert2payAPI
from webhook_sender import WebhookSender
import logging

logger = logging.getLogger(__name__)

class MessageHandlers:
    """Обработчики сообщений для различных состояний"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_invoice_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка состояний создания инвойса"""
        user = update.effective_user
        message_text = update.message.text.strip()
        
        # Отладочная информация
        print(f"DEBUG: handle_invoice_states called with message: '{message_text}'")
        print(f"DEBUG: Current states: {context.user_data}")
        
        if context.user_data.get(UserState.WAITING_FOR_INVOICE_ID.value):
            print("DEBUG: Processing WAITING_FOR_INVOICE_ID")
            return await self._handle_invoice_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_CLIENT_ID.value):
            print("DEBUG: Processing WAITING_FOR_CLIENT_ID")
            return await self._handle_client_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_AMOUNT.value):
            print("DEBUG: Processing WAITING_FOR_AMOUNT")
            return await self._handle_amount_input(update, context, message_text)
        
        print("DEBUG: No invoice state matched")
        return False
    
    async def handle_payout_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка состояний создания выплаты"""
        user = update.effective_user
        message_text = update.message.text.strip()
        
        if context.user_data.get(UserState.WAITING_FOR_PAYOUT_ORDER_ID.value):
            return await self._handle_payout_order_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value):
            return await self._handle_payout_client_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_IBAN_ACCOUNT.value):
            return await self._handle_iban_account_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_IBAN_INN.value):
            return await self._handle_iban_inn_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_SURNAME.value):
            return await self._handle_surname_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_NAME.value):
            return await self._handle_name_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_MIDDLENAME.value):
            return await self._handle_middlename_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_PURPOSE.value):
            return await self._handle_purpose_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_PAYOUT_AMOUNT.value):
            return await self._handle_payout_amount_input(update, context, message_text)
        
        return False
    
    async def handle_admin_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка состояний админа"""
        user = update.effective_user
        username = user.username
        message_text = update.message.text.strip()
        
        if not self.bot.is_admin(username):
            return False
        
        if context.user_data.get(UserState.WAITING_FOR_USERNAME.value):
            return await self._handle_admin_username_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_SHOP_ID.value):
            return await self._handle_admin_shop_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_SHOP_API_KEY.value):
            return await self._handle_admin_shop_api_key_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_ORDER_ID_TAG.value):
            return await self._handle_admin_order_id_tag_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_DELETE_USERNAME.value):
            return await self._handle_admin_delete_username_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_DELETE_SHOP_ID.value):
            return await self._handle_admin_delete_shop_id_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_INFO_EDIT.value):
            return await self._handle_admin_info_edit_input(update, context, message_text)
        elif context.user_data.get(UserState.WAITING_FOR_BROADCAST.value):
            return await self._handle_admin_broadcast_input(update, context, message_text)
        
        return False
    
    async def handle_logout_state(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка состояния выхода"""
        user = update.effective_user
        username = user.username
        message_text = update.message.text.strip()
        
        if context.user_data.get(UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value):
            if message_text == f"@{username}":
                # Подтверждение выхода
                self.bot.revoke_merchant_access(user.id)
                StateManager.clear_logout_states(context)
                
                # Отправляем webhook о выходе пользователя
                user_info = {
                    "user_id": user.id,
                    "username": username,
                    "shop_id": None  # После выхода shop_id недоступен
                }
                await WebhookSender.send_user_action_webhook("logout", user_info)
                
                message = "✅ Ваш аккаунт успешно отвязан от Бота."
                keyboard = [
                    [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                    [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(message, reply_markup=reply_markup)
                return True
            else:
                # Неверное подтверждение
                message = "❌ Неверный username. Попробуйте ещё раз или нажмите 'Отмена'."
                keyboard = [
                    [InlineKeyboardButton("Отмена", callback_data="logout_cancel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, reply_markup=reply_markup)
                return True
        
        return False
    
    # Приватные методы для обработки состояний инвойса
    async def _handle_invoice_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода ID инвойса"""
        context.user_data['invoice_order_id'] = message_text
        context.user_data['current_state'] = UserState.WAITING_FOR_CLIENT_ID.value
        context.user_data[UserState.WAITING_FOR_INVOICE_ID.value] = False
        context.user_data[UserState.WAITING_FOR_CLIENT_ID.value] = True
        
        message = f"🎰 Укажите ID Клиента\n\nORDER ID: {message_text}"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_client_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода ID клиента"""
        context.user_data['invoice_client_id'] = message_text
        context.user_data['current_state'] = UserState.WAITING_FOR_AMOUNT.value
        context.user_data[UserState.WAITING_FOR_CLIENT_ID.value] = False
        context.user_data[UserState.WAITING_FOR_AMOUNT.value] = True
        
        invoice_order_id = context.user_data.get('invoice_order_id', 'Не указан')
        message = f"🎰 Укажите сумму\n\nORDER ID: {invoice_order_id}\nID Клиента: {message_text}"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода суммы"""
        try:
            amount = float(message_text)
            context.user_data['invoice_amount'] = amount
            context.user_data['current_state'] = None  # Завершаем флоу
            context.user_data[UserState.WAITING_FOR_AMOUNT.value] = False
            
            invoice_order_id = context.user_data.get('invoice_order_id', 'Не указан')
            client_id = context.user_data.get('invoice_client_id', 'Не указан')
            
            message = f"🎰 Заявка на инвойс\n\n• ID инвойса: {invoice_order_id}\n• ID Клиента: {client_id}\n• Сумма: {amount} UAH"
            
            inline_keyboard = [
                [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_invoice"),
                 InlineKeyboardButton("❌ Отмена", callback_data="cancel_invoice")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)
            
            keyboard = [[KeyboardButton("◀️ Главное меню")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(message, reply_markup=inline_markup)
            await update.message.reply_text("◀️ Главное меню", reply_markup=reply_markup)
            return True
        except ValueError:
            await update.message.reply_text("❌ Ошибка: Введите корректную сумму (например: 500.75)")
            return True
    
    # Приватные методы для обработки состояний выплаты
    async def _handle_payout_order_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода ID заявки"""
        context.user_data['payout_order_id'] = message_text
        context.user_data[UserState.WAITING_FOR_PAYOUT_ORDER_ID.value] = False
        context.user_data[UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value] = True
        
        message = "💎 Укажите ID Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_payout_client_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода ID клиента для выплаты"""
        context.user_data['payout_client_id'] = message_text
        context.user_data[UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value] = False
        context.user_data[UserState.WAITING_FOR_IBAN_ACCOUNT.value] = True
        
        message = "💎 Укажите IBAN-счет Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_iban_account_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода IBAN-счета"""
        context.user_data['payout_iban_account'] = message_text
        context.user_data[UserState.WAITING_FOR_IBAN_ACCOUNT.value] = False
        context.user_data[UserState.WAITING_FOR_IBAN_INN.value] = True
        
        message = "💎 Укажите ИНН Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_iban_inn_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода ИНН"""
        context.user_data['payout_iban_inn'] = message_text
        context.user_data[UserState.WAITING_FOR_IBAN_INN.value] = False
        context.user_data[UserState.WAITING_FOR_SURNAME.value] = True
        
        message = "💎 Укажите фамилию Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_surname_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода фамилии"""
        context.user_data['payout_surname'] = message_text
        context.user_data[UserState.WAITING_FOR_SURNAME.value] = False
        context.user_data[UserState.WAITING_FOR_NAME.value] = True
        
        message = "💎 Укажите имя Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода имени"""
        context.user_data['payout_name'] = message_text
        context.user_data[UserState.WAITING_FOR_NAME.value] = False
        context.user_data[UserState.WAITING_FOR_MIDDLENAME.value] = True
        
        message = "💎 Укажите отчество Клиента"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_middlename_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода отчества"""
        context.user_data['payout_middlename'] = message_text
        context.user_data[UserState.WAITING_FOR_MIDDLENAME.value] = False
        context.user_data[UserState.WAITING_FOR_PURPOSE.value] = True
        
        message = "💎 Укажите назначение платежа Клиента\n\nВы можете также выбрать один из стандартных вариантов"
        
        inline_keyboard = [
            [InlineKeyboardButton("Поповнення рахунку", callback_data="purpose_popovnennya"),
             InlineKeyboardButton("Повернення боргу", callback_data="purpose_povorennya"),
             InlineKeyboardButton("Переказ коштів", callback_data="purpose_perekaz")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(message, reply_markup=inline_markup)
        await update.message.reply_text(".", reply_markup=reply_markup)
        return True
    
    async def _handle_purpose_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода назначения платежа"""
        context.user_data['payout_purpose'] = message_text
        context.user_data[UserState.WAITING_FOR_PURPOSE.value] = False
        context.user_data[UserState.WAITING_FOR_PAYOUT_AMOUNT.value] = True
        
        message = "💎 Укажите сумму"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_payout_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода суммы для выплаты"""
        try:
            amount = float(message_text)
            context.user_data['payout_amount'] = amount
            context.user_data[UserState.WAITING_FOR_PAYOUT_AMOUNT.value] = False
            
            payout_order_id = context.user_data.get('payout_order_id', 'Не указан')
            client_id = context.user_data.get('payout_client_id', 'Не указан')
            iban_account = context.user_data.get('payout_iban_account', 'Не указан')
            iban_inn = context.user_data.get('payout_iban_inn', 'Не указан')
            surname = context.user_data.get('payout_surname', 'Не указан')
            name = context.user_data.get('payout_name', 'Не указан')
            middlename = context.user_data.get('payout_middlename', 'Не указан')
            purpose = context.user_data.get('payout_purpose', 'Не указан')
            
            message = f"💎 Заявка на выплату\n\n• ID заявки: {payout_order_id}\n• ID Клиента: {client_id}\n• Номер iBAN-счета: {iban_account}\n• ИНН: {iban_inn}\n• ФИО: {surname} {name} {middlename}\n• Назначение платежа: {purpose}\n• Сумма: {amount} UAH"
            
            inline_keyboard = [
                [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_payout"),
                 InlineKeyboardButton("❌ Отмена", callback_data="cancel_payout")]
            ]
            inline_markup = InlineKeyboardMarkup(inline_keyboard)
            
            keyboard = [[KeyboardButton("◀️ Главное меню")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(message, reply_markup=inline_markup)
            await update.message.reply_text("◀️ Главное меню", reply_markup=reply_markup)
            return True
        except ValueError:
            await update.message.reply_text("❌ Ошибка: Введите корректную сумму (например: 1000.35)")
            return True
    
    # Приватные методы для обработки состояний админа
    async def _handle_admin_username_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода username админом"""
        context.user_data['temp_username'] = message_text
        context.user_data[UserState.WAITING_FOR_USERNAME.value] = False
        context.user_data[UserState.WAITING_FOR_SHOP_ID.value] = True
        
        message = f"👤 Укажите shop_id для пользователя @{message_text}"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_admin_shop_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода shop_id админом"""
        context.user_data['temp_shop_id'] = message_text
        context.user_data[UserState.WAITING_FOR_SHOP_ID.value] = False
        context.user_data[UserState.WAITING_FOR_SHOP_API_KEY.value] = True
        
        username = context.user_data.get('temp_username', 'Не указан')
        message = f"👤 Укажите shop_api_key для пользователя @{username}\n\nShop ID: {message_text}"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_admin_shop_api_key_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода shop_api_key админом"""
        context.user_data['temp_shop_api_key'] = message_text
        context.user_data[UserState.WAITING_FOR_SHOP_API_KEY.value] = False
        context.user_data[UserState.WAITING_FOR_ORDER_ID_TAG.value] = True
        
        username = context.user_data.get('temp_username', 'Не указан')
        shop_id = context.user_data.get('temp_shop_id', 'Не указан')
        message = f"👤 Укажите значение, которое будет привязано к этому Telegram-аккаунту, как ORDER ID TAG при создании инвойса или выплаты.\n\nUsername: @{username}\nShop ID: {shop_id}\nShop API Key: {message_text}"
        
        inline_keyboard = [
            [InlineKeyboardButton("Пропустить", callback_data="skip_order_id_tag")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(message, reply_markup=inline_markup)
        await update.message.reply_text(".", reply_markup=reply_markup)
        return True
    
    async def _handle_admin_order_id_tag_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода order_id_tag админом"""
        username = context.user_data.get('temp_username', 'Не указан')
        shop_id = context.user_data.get('temp_shop_id', 'Не указан')
        shop_api_key = context.user_data.get('temp_shop_api_key', 'Не указан')
        order_id_tag = message_text
        
        # Добавляем пользователя
        success = self.bot.add_user(username, shop_id, shop_api_key, order_id_tag)
        
        if success:
            # Отправляем webhook о добавлении пользователя
            user_info = {
                "user_id": None,  # Пользователь еще не зарегистрирован в Telegram
                "username": username,
                "shop_id": shop_id
            }
            additional_data = {
                "shop_api_key": shop_api_key,
                "order_id_tag": order_id_tag,
                "added_by_admin": True
            }
            await WebhookSender.send_user_action_webhook("added", user_info, additional_data)
            
            message = f"✅ Пользователь @{username} успешно добавлен!\n\nShop ID: {shop_id}\nShop API Key: {shop_api_key}\nOrder ID Tag: {order_id_tag}"
        else:
            message = f"❌ Ошибка при добавлении пользователя @{username}"
        
        # Возвращаем в меню управления пользователями
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_admin_states(context)
        return True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Основной обработчик сообщений"""
        user = update.effective_user
        message_text = update.message.text
        current_state = context.user_data.get('current_state')
        
        # Обработка состояний создания инвойса
        if current_state in [UserState.WAITING_FOR_INVOICE_ID.value, 
                           UserState.WAITING_FOR_CLIENT_ID.value,
                           UserState.WAITING_FOR_AMOUNT.value]:
            return await self.handle_invoice_states(update, context)
        
        # Обработка состояний создания выплаты
        elif current_state in [UserState.WAITING_FOR_PAYOUT_ORDER_ID.value,
                             UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value,
                             UserState.WAITING_FOR_IBAN_ACCOUNT.value,
                             UserState.WAITING_FOR_IBAN_INN.value,
                             UserState.WAITING_FOR_SURNAME.value,
                             UserState.WAITING_FOR_NAME.value,
                             UserState.WAITING_FOR_MIDDLENAME.value,
                             UserState.WAITING_FOR_PURPOSE.value,
                             UserState.WAITING_FOR_PAYOUT_AMOUNT.value]:
            return await self.handle_payout_states(update, context)
        
        # Обработка состояний админа
        elif current_state in [UserState.WAITING_FOR_ADMIN_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_API_KEY.value,
                             UserState.WAITING_FOR_ADMIN_ORDER_TAG.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_BROADCAST.value,
                             UserState.WAITING_FOR_INFO_EDIT.value]:
            return await self.handle_admin_states(update, context)
        
        # Обработка состояния выхода из аккаунта
        elif current_state == UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value:
            return await self.handle_logout_state(update, context)
        
        # Обработка команд мерчанта
        elif message_text in ["👤 Профиль", "📄 Информация", "🎰 Создать инвойс", "💎 Создать выплату", "❌ Выйти из аккаунта"]:
            return await self.handle_merchant_commands(update, context)
        
        # Обработка команд админа
        elif message_text in ["👤 Пользователи", "✉️ Создать рассылку", "👤 Добавить пользователя", "❌ Удалить пользователя"]:
            return await self.handle_admin_commands(update, context)
        
        return False
    
    async def handle_merchant_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд мерчанта"""
        from handlers.merchant_commands import ProfileCommand, InfoCommand, CreateInvoiceCommand, CreatePayoutCommand, LogoutCommand
        
        if update.message.text == "👤 Профиль":
            command = ProfileCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "📄 Информация":
            command = InfoCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "🎰 Создать инвойс":
            command = CreateInvoiceCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "💎 Создать выплату":
            command = CreatePayoutCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Выйти из аккаунта":
            command = LogoutCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def handle_admin_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд админа"""
        from handlers.admin_commands import ShowUsersCommand, CreateBroadcastCommand, AddUserCommand, DeleteUserCommand
        
        if update.message.text == "👤 Пользователи":
            command = ShowUsersCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "✉️ Создать рассылку":
            command = CreateBroadcastCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "👤 Добавить пользователя":
            command = AddUserCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Удалить пользователя":
            command = DeleteUserCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def _handle_admin_delete_username_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода username для удаления"""
        context.user_data['delete_username'] = message_text
        context.user_data[UserState.WAITING_FOR_DELETE_USERNAME.value] = False
        context.user_data[UserState.WAITING_FOR_DELETE_SHOP_ID.value] = True
        
        message = f"Для подтверждения действия отправьте shop_id, к которому был привязан пользователь @{message_text}."
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        return True
    
    async def _handle_admin_delete_shop_id_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка ввода shop_id для подтверждения удаления"""
        username = context.user_data.get('delete_username', 'Не указан')
        shop_id = message_text
        
        # Проверяем, что shop_id соответствует username
        user_data = self.bot.get_user_by_username(username)
        if user_data and user_data[2] == shop_id:  # user_data[2] это shop_id
            # Отправляем webhook перед удалением
            user_info = {
                "user_id": user_data[0],
                "username": username,
                "shop_id": shop_id
            }
            additional_data = {
                "shop_api_key": user_data[3],
                "order_id_tag": user_data[4],
                "deleted_by_admin": True
            }
            await WebhookSender.send_user_action_webhook("deleted", user_info, additional_data)
            
            # Удаляем пользователя
            self.bot.delete_user(username)
            
            message = "❌ Пользователь успешно удален"
            
            # Показываем обновленный список пользователей
            users = self.bot.get_all_users()
            if users:
                user_list = "\n".join([f"{i+1}) @{user[1]} shop_id: {user[2]} shop_api_key: {user[3]}" for i, user in enumerate(users)])
                message += f"\n\n👤 Пользователи, у которых есть доступ к Боту:\n{user_list}"
            else:
                message += "\n\n👤 Пользователи, у которых есть доступ к Боту: Нет активных пользователей"
            
            # Возвращаем в меню управления пользователями
            keyboard = [
                [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
                [KeyboardButton("◀️ Главное меню")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            # Неверный shop_id
            message = "⚠️ Ошибка\n\nПодтвердить удаление пользователя не удалось. Указанный shop_id не привязан к заявленному username."
            
            # Возвращаем в главное меню админа
            keyboard = [
                [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_admin_states(context)
        return True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Основной обработчик сообщений"""
        user = update.effective_user
        message_text = update.message.text
        current_state = context.user_data.get('current_state')
        
        # Обработка состояний создания инвойса
        if current_state in [UserState.WAITING_FOR_INVOICE_ID.value, 
                           UserState.WAITING_FOR_CLIENT_ID.value,
                           UserState.WAITING_FOR_AMOUNT.value]:
            return await self.handle_invoice_states(update, context)
        
        # Обработка состояний создания выплаты
        elif current_state in [UserState.WAITING_FOR_PAYOUT_ORDER_ID.value,
                             UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value,
                             UserState.WAITING_FOR_IBAN_ACCOUNT.value,
                             UserState.WAITING_FOR_IBAN_INN.value,
                             UserState.WAITING_FOR_SURNAME.value,
                             UserState.WAITING_FOR_NAME.value,
                             UserState.WAITING_FOR_MIDDLENAME.value,
                             UserState.WAITING_FOR_PURPOSE.value,
                             UserState.WAITING_FOR_PAYOUT_AMOUNT.value]:
            return await self.handle_payout_states(update, context)
        
        # Обработка состояний админа
        elif current_state in [UserState.WAITING_FOR_ADMIN_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_API_KEY.value,
                             UserState.WAITING_FOR_ADMIN_ORDER_TAG.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_BROADCAST.value,
                             UserState.WAITING_FOR_INFO_EDIT.value]:
            return await self.handle_admin_states(update, context)
        
        # Обработка состояния выхода из аккаунта
        elif current_state == UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value:
            return await self.handle_logout_state(update, context)
        
        # Обработка команд мерчанта
        elif message_text in ["👤 Профиль", "📄 Информация", "🎰 Создать инвойс", "💎 Создать выплату", "❌ Выйти из аккаунта"]:
            return await self.handle_merchant_commands(update, context)
        
        # Обработка команд админа
        elif message_text in ["👤 Пользователи", "✉️ Создать рассылку", "👤 Добавить пользователя", "❌ Удалить пользователя"]:
            return await self.handle_admin_commands(update, context)
        
        return False
    
    async def handle_merchant_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд мерчанта"""
        from handlers.merchant_commands import ProfileCommand, InfoCommand, CreateInvoiceCommand, CreatePayoutCommand, LogoutCommand
        
        if update.message.text == "👤 Профиль":
            command = ProfileCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "📄 Информация":
            command = InfoCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "🎰 Создать инвойс":
            command = CreateInvoiceCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "💎 Создать выплату":
            command = CreatePayoutCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Выйти из аккаунта":
            command = LogoutCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def handle_admin_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд админа"""
        from handlers.admin_commands import ShowUsersCommand, CreateBroadcastCommand, AddUserCommand, DeleteUserCommand
        
        if update.message.text == "👤 Пользователи":
            command = ShowUsersCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "✉️ Создать рассылку":
            command = CreateBroadcastCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "👤 Добавить пользователя":
            command = AddUserCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Удалить пользователя":
            command = DeleteUserCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def _handle_admin_info_edit_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка редактирования информационного блока"""
        self.bot.update_info_content(message_text)
        
        message = f"✅ Информационный блок успешно обновлен!\n\nНовое содержимое:\n\n{message_text}"
        
        # Возвращаем в главное меню админа
        keyboard = [
            [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_admin_states(context)
        return True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Основной обработчик сообщений"""
        user = update.effective_user
        message_text = update.message.text
        current_state = context.user_data.get('current_state')
        
        # Обработка состояний создания инвойса
        if current_state in [UserState.WAITING_FOR_INVOICE_ID.value, 
                           UserState.WAITING_FOR_CLIENT_ID.value,
                           UserState.WAITING_FOR_AMOUNT.value]:
            return await self.handle_invoice_states(update, context)
        
        # Обработка состояний создания выплаты
        elif current_state in [UserState.WAITING_FOR_PAYOUT_ORDER_ID.value,
                             UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value,
                             UserState.WAITING_FOR_IBAN_ACCOUNT.value,
                             UserState.WAITING_FOR_IBAN_INN.value,
                             UserState.WAITING_FOR_SURNAME.value,
                             UserState.WAITING_FOR_NAME.value,
                             UserState.WAITING_FOR_MIDDLENAME.value,
                             UserState.WAITING_FOR_PURPOSE.value,
                             UserState.WAITING_FOR_PAYOUT_AMOUNT.value]:
            return await self.handle_payout_states(update, context)
        
        # Обработка состояний админа
        elif current_state in [UserState.WAITING_FOR_ADMIN_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_API_KEY.value,
                             UserState.WAITING_FOR_ADMIN_ORDER_TAG.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_BROADCAST.value,
                             UserState.WAITING_FOR_INFO_EDIT.value]:
            return await self.handle_admin_states(update, context)
        
        # Обработка состояния выхода из аккаунта
        elif current_state == UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value:
            return await self.handle_logout_state(update, context)
        
        # Обработка команд мерчанта
        elif message_text in ["👤 Профиль", "📄 Информация", "🎰 Создать инвойс", "💎 Создать выплату", "❌ Выйти из аккаунта"]:
            return await self.handle_merchant_commands(update, context)
        
        # Обработка команд админа
        elif message_text in ["👤 Пользователи", "✉️ Создать рассылку", "👤 Добавить пользователя", "❌ Удалить пользователя"]:
            return await self.handle_admin_commands(update, context)
        
        return False
    
    async def handle_merchant_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд мерчанта"""
        from handlers.merchant_commands import ProfileCommand, InfoCommand, CreateInvoiceCommand, CreatePayoutCommand, LogoutCommand
        
        if update.message.text == "👤 Профиль":
            command = ProfileCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "📄 Информация":
            command = InfoCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "🎰 Создать инвойс":
            command = CreateInvoiceCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "💎 Создать выплату":
            command = CreatePayoutCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Выйти из аккаунта":
            command = LogoutCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def handle_admin_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд админа"""
        from handlers.admin_commands import ShowUsersCommand, CreateBroadcastCommand, AddUserCommand, DeleteUserCommand
        
        if update.message.text == "👤 Пользователи":
            command = ShowUsersCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "✉️ Создать рассылку":
            command = CreateBroadcastCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "👤 Добавить пользователя":
            command = AddUserCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Удалить пользователя":
            command = DeleteUserCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def _handle_admin_broadcast_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Обработка создания рассылки"""
        users = self.bot.get_all_users()
        if users:
            for user in users:
                try:
                    # Отправляем сообщение каждому пользователю
                    await context.bot.send_message(chat_id=user[0], text=message_text)
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения пользователю {user[1]}: {e}")
            
            message = f"✅ Рассылка отправлена {len(users)} пользователям."
        else:
            message = "❌ Нет пользователей для рассылки."
        
        # Возвращаем в главное меню админа
        keyboard = [
            [KeyboardButton("👤 Пользователи"), KeyboardButton("✉️ Создать рассылку")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_admin_states(context)
        return True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Основной обработчик сообщений"""
        user = update.effective_user
        message_text = update.message.text
        current_state = context.user_data.get('current_state')
        
        # Обработка состояний создания инвойса
        if current_state in [UserState.WAITING_FOR_INVOICE_ID.value, 
                           UserState.WAITING_FOR_CLIENT_ID.value,
                           UserState.WAITING_FOR_AMOUNT.value]:
            return await self.handle_invoice_states(update, context)
        
        # Обработка состояний создания выплаты
        elif current_state in [UserState.WAITING_FOR_PAYOUT_ORDER_ID.value,
                             UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value,
                             UserState.WAITING_FOR_IBAN_ACCOUNT.value,
                             UserState.WAITING_FOR_IBAN_INN.value,
                             UserState.WAITING_FOR_SURNAME.value,
                             UserState.WAITING_FOR_NAME.value,
                             UserState.WAITING_FOR_MIDDLENAME.value,
                             UserState.WAITING_FOR_PURPOSE.value,
                             UserState.WAITING_FOR_PAYOUT_AMOUNT.value]:
            return await self.handle_payout_states(update, context)
        
        # Обработка состояний админа
        elif current_state in [UserState.WAITING_FOR_ADMIN_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_API_KEY.value,
                             UserState.WAITING_FOR_ADMIN_ORDER_TAG.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_USERNAME.value,
                             UserState.WAITING_FOR_ADMIN_DELETE_SHOP_ID.value,
                             UserState.WAITING_FOR_ADMIN_BROADCAST.value,
                             UserState.WAITING_FOR_INFO_EDIT.value]:
            return await self.handle_admin_states(update, context)
        
        # Обработка состояния выхода из аккаунта
        elif current_state == UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value:
            return await self.handle_logout_state(update, context)
        
        # Обработка команд мерчанта
        elif message_text in ["👤 Профиль", "📄 Информация", "🎰 Создать инвойс", "💎 Создать выплату", "❌ Выйти из аккаунта"]:
            return await self.handle_merchant_commands(update, context)
        
        # Обработка команд админа
        elif message_text in ["👤 Пользователи", "✉️ Создать рассылку", "👤 Добавить пользователя", "❌ Удалить пользователя"]:
            return await self.handle_admin_commands(update, context)
        
        return False
    
    async def handle_merchant_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд мерчанта"""
        from handlers.merchant_commands import ProfileCommand, InfoCommand, CreateInvoiceCommand, CreatePayoutCommand, LogoutCommand
        
        if update.message.text == "👤 Профиль":
            command = ProfileCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "📄 Информация":
            command = InfoCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "🎰 Создать инвойс":
            command = CreateInvoiceCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "💎 Создать выплату":
            command = CreatePayoutCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Выйти из аккаунта":
            command = LogoutCommand(self.bot)
            return await command.handle(update, context)
        
        return False
    
    async def handle_admin_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка команд админа"""
        from handlers.admin_commands import ShowUsersCommand, CreateBroadcastCommand, AddUserCommand, DeleteUserCommand
        
        if update.message.text == "👤 Пользователи":
            command = ShowUsersCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "✉️ Создать рассылку":
            command = CreateBroadcastCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "👤 Добавить пользователя":
            command = AddUserCommand(self.bot)
            return await command.handle(update, context)
        elif update.message.text == "❌ Удалить пользователя":
            command = DeleteUserCommand(self.bot)
            return await command.handle(update, context)
        
        return False
