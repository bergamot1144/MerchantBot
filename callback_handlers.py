"""
Обработчики callback кнопок
"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from states import UserState, StateManager
from api_client import Konvert2payAPI
import logging

logger = logging.getLogger(__name__)

class CallbackHandlers:
    """Обработчики callback кнопок"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        data = query.data
        
        # Обработка выбора метода инвойса
        if data in ["invoice_method_card", "invoice_method_oneclick", "invoice_method_iban"]:
            return await self._handle_invoice_method_selection(query, context, data)
        
        # Обработка кнопок назначения платежа
        elif data in ["purpose_popovnennya", "purpose_povorennya", "purpose_perekaz"]:
            return await self._handle_purpose_selection(query, context, data)
        
        # Обработка кнопок подтверждения/отмены инвойса
        elif data in ["confirm_invoice", "cancel_invoice"]:
            return await self._handle_invoice_confirmation(query, context, data)
        
        # Обработка кнопок подтверждения/отмены выплаты
        elif data in ["confirm_payout", "cancel_payout"]:
            return await self._handle_payout_confirmation(query, context, data)
        
        # Обработка кнопки пропуска order_id_tag
        elif data == "skip_order_id_tag":
            return await self._handle_skip_order_id_tag(query, context)
        
        # Обработка кнопки отмены выхода
        elif data == "logout_cancel":
            return await self._handle_logout_cancel(query, context)
        
        return False
    
    async def _handle_invoice_method_selection(self, query, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Обработка выбора метода инвойса"""
        user_id = query.from_user.id
        settings = self.bot.get_merchant_settings(user_id)
        
        if not settings:
            await query.edit_message_text("❌ Ошибка: Настройки мерчанта не найдены.")
            return True
            
        order_id_tag = settings[3]
        
        if order_id_tag:
            # Если есть order_id_tag, пропускаем первый шаг
            auto_order_id = self.bot.get_next_order_id(user_id)
            context.user_data['invoice_order_id'] = auto_order_id
            context.user_data[UserState.WAITING_FOR_CLIENT_ID.value] = True
            
            message = f"🎰 Укажите ID Клиента\n\nORDER ID автоматически установлен: {auto_order_id}"
            keyboard = [[KeyboardButton("◀️ Главное меню")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text(" ", reply_markup=reply_markup)
        else:
            # Если нет order_id_tag, запрашиваем ID инвойса
            context.user_data[UserState.WAITING_FOR_INVOICE_ID.value] = True
            
            message = "🎰 Укажите ID инвойса"
            keyboard = [[KeyboardButton("◀️ Главное меню")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text(" ", reply_markup=reply_markup)
        
        return True
    
    async def _handle_purpose_selection(self, query, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Обработка выбора назначения платежа"""
        purpose_map = {
            "purpose_popovnennya": "Поповнення рахунку",
            "purpose_povorennya": "Повернення боргу",
            "purpose_perekaz": "Переказ коштів"
        }
        
        context.user_data['payout_purpose'] = purpose_map[data]
        context.user_data[UserState.WAITING_FOR_PURPOSE.value] = False
        context.user_data[UserState.WAITING_FOR_PAYOUT_AMOUNT.value] = True
        
        message = "💎 Укажите сумму"
        keyboard = [[KeyboardButton("◀️ Главное меню")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text(message)
        await query.message.reply_text("◀️ Главное меню", reply_markup=reply_markup)
        return True
    
    async def _handle_invoice_confirmation(self, query, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Обработка подтверждения/отмены инвойса"""
        if data == "confirm_invoice":
            return await self._confirm_invoice(query, context)
        elif data == "cancel_invoice":
            return await self._cancel_invoice(query, context)
        return False
    
    async def _handle_payout_confirmation(self, query, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Обработка подтверждения/отмены выплаты"""
        if data == "confirm_payout":
            return await self._confirm_payout(query, context)
        elif data == "cancel_payout":
            return await self._cancel_payout(query, context)
        return False
    
    async def _confirm_invoice(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение создания инвойса"""
        user_id = query.from_user.id
        settings = self.bot.get_merchant_settings(user_id)
        
        if not settings:
            await query.edit_message_text("❌ Ошибка: Настройки мерчанта не найдены.")
            return True
            
        shop_id = settings[1]
        shop_api_key = settings[2]
        invoice_order_id = context.user_data.get('invoice_order_id')
        client_id = context.user_data.get('invoice_client_id')
        amount = context.user_data.get('invoice_amount')
        
        # Подготавливаем информацию о пользователе для webhook
        user_info = {
            "user_id": user_id,
            "username": query.from_user.username,
            "shop_id": shop_id
        }
        
        # Создаем инвойс через API
        result = await Konvert2payAPI.create_invoice(shop_id, shop_api_key, invoice_order_id, client_id, amount, user_info)
        
        if result.get('Success'):
            # Успешное создание инвойса
            data = result.get('Data', {})
            invoice_id = data.get('invoice_id')
            pay_url = data.get('pay_url')
            currency = data.get('currency', 'UAH')
            
            message = f"✅ Успех\n\nИнвойс был создан.\n\n• ID ордера: {invoice_id}\n• ID инвойса: {invoice_order_id}\n• ID Клиента: {client_id}\n• Сумма: {amount} {currency}\n\nСсылка на платежное окно: {pay_url}"
            
            # Возвращаем в главное меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        else:
            # Ошибка создания инвойса
            error = result.get('Error', {})
            error_code = error.get('Code', 'Unknown')
            error_message = error.get('Message', 'Unknown error')
            
            message = f"⚠️ Ошибка\n\nИнвойс не был создан. Проверьте данные заявки и попробуйте ещё раз.\n\nКод ошибки: {error_code}\nСтатус: {error_message}"
            
            # Возвращаем в главное меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояние
        StateManager.clear_invoice_states(context)
        return True
    
    async def _cancel_invoice(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Отмена создания инвойса"""
        message = "❌ Создание инвойса отменено"
        
        # Возвращаем в главное меню мерчанта
        keyboard = [
            [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
            [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text(message)
        await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояние
        StateManager.clear_invoice_states(context)
        return True
    
    async def _confirm_payout(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение создания выплаты"""
        user_id = query.from_user.id
        settings = self.bot.get_merchant_settings(user_id)
        
        if not settings:
            await query.edit_message_text("❌ Ошибка: Настройки мерчанта не найдены.")
            return True
            
        shop_id = settings[1]
        shop_api_key = settings[2]
        payout_order_id = context.user_data.get('payout_order_id')
        client_id = context.user_data.get('payout_client_id')
        iban_account = context.user_data.get('payout_iban_account')
        iban_inn = context.user_data.get('payout_iban_inn')
        surname = context.user_data.get('payout_surname')
        name = context.user_data.get('payout_name')
        middlename = context.user_data.get('payout_middlename')
        purpose = context.user_data.get('payout_purpose')
        amount = context.user_data.get('payout_amount')
        
        # Подготавливаем информацию о пользователе для webhook
        user_info = {
            "user_id": user_id,
            "username": query.from_user.username,
            "shop_id": shop_id
        }
        
        # Создаем выплату через API
        result = await Konvert2payAPI.create_payout(shop_id, shop_api_key, payout_order_id, client_id, 
                                                   iban_account, iban_inn, surname, name, middlename, 
                                                   purpose, amount, user_info)
        
        if result.get('Success'):
            # Успешное создание выплаты
            data = result.get('Data', {})
            withdrawal_id = data.get('withdrawal_id')
            currency = data.get('currency', 'UAH')
            
            message = f"✅ Успех\n\nВыплата была создана.\n\n• ID выплаты: {withdrawal_id}\n• ID заявки: {payout_order_id}\n• ID Клиента: {client_id}\n• Номер iBAN-счета: {iban_account}\n• ИНН: {iban_inn}\n• ФИО: {surname} {name} {middlename}\n• Назначение платежа: {purpose}\n• Сумма: {amount} {currency}"
            
            # Возвращаем в главное меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        else:
            # Ошибка создания выплаты
            error = result.get('Error', {})
            error_code = error.get('Code', 'Unknown')
            error_message = error.get('Message', 'Unknown error')
            
            message = f"⚠️ Ошибка\n\nВыплата не была создана. Проверьте данные заявки и попробуйте ещё раз.\n\nКод ошибки: {error_code}\nСтатус: {error_message}"
            
            # Возвращаем в главное меню мерчанта
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
                [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.edit_message_text(message)
            await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояние
        StateManager.clear_payout_states(context)
        return True
    
    async def _cancel_payout(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Отмена создания выплаты"""
        message = "❌ Создание выплаты отменено"
        
        # Возвращаем в главное меню мерчанта
        keyboard = [
            [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
            [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text(message)
        await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояние
        StateManager.clear_payout_states(context)
        return True
    
    async def _handle_skip_order_id_tag(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Обработка пропуска order_id_tag"""
        username = context.user_data.get('temp_username', 'Не указан')
        shop_id = context.user_data.get('temp_shop_id', 'Не указан')
        shop_api_key = context.user_data.get('temp_shop_api_key', 'Не указан')
        
        # Добавляем пользователя без order_id_tag
        success = self.bot.add_user(username, shop_id, shop_api_key, None)
        
        if success:
            message = f"✅ Пользователь @{username} успешно добавлен!\n\nShop ID: {shop_id}\nShop API Key: {shop_api_key}\nOrder ID Tag: Не указан"
        else:
            message = f"❌ Ошибка при добавлении пользователя @{username}"
        
        # Возвращаем в меню управления пользователями
        keyboard = [
            [KeyboardButton("👤 Добавить пользователя"), KeyboardButton("❌ Удалить пользователя")],
            [KeyboardButton("◀️ Главное меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text(message)
        await query.message.reply_text("◀️ Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_admin_states(context)
        return True
    
    async def _handle_logout_cancel(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Обработка отмены выхода"""
        message = "❌ Выход из аккаунта отменен"
        
        # Возвращаем в главное меню мерчанта
        keyboard = [
            [KeyboardButton("👤 Профиль"), KeyboardButton("📄 Информация")],
            [KeyboardButton("🎰 Создать инвойс"), KeyboardButton("💎 Создать выплату")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text(message)
        await query.message.reply_text("👨🏻‍💻 Главное меню", reply_markup=reply_markup)
        
        # Очищаем состояния
        StateManager.clear_logout_states(context)
        return True
