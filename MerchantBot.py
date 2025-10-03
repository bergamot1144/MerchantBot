"""
Рефакторированный Telegram бот для мерчантов Konvert2pay
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT

# Импорты новых модулей
from db_utils import DatabaseManager, UserManager, InfoManager, OrderManager
from keyboard_manager import KeyboardManager
from constants import Messages, Buttons, CallbackData
from states import UserState, StateManager
from message_handlers import MessageHandlers
from callback_handlers import CallbackHandlers

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class MerchantBot:
    """Основной класс бота для работы с мерчантами"""
    
    def __init__(self):
        # Инициализация менеджеров
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.info_manager = InfoManager(self.db_manager)
        self.order_manager = OrderManager(self.db_manager)
        self.keyboard_manager = KeyboardManager()
        
        # Инициализация обработчиков
        self.message_handlers = MessageHandlers(self)
        self.callback_handlers = CallbackHandlers(self)
        
        # Инициализация базы данных
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_merchant BOOLEAN DEFAULT FALSE,
                    merchant_settings TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание таблицы настроек мерчанта
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merchant_settings (
                    user_id INTEGER PRIMARY KEY,
                    shop_id TEXT,
                    shop_api_key TEXT,
                    order_id_tag TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Создание таблицы информационного блока
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS info_block (
                    id INTEGER PRIMARY KEY,
                    content TEXT
                )
            ''')
            
            # Создание таблицы счетчиков заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_counters (
                    order_id_tag TEXT PRIMARY KEY,
                    counter INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    # Методы для совместимости с существующим кодом
    def is_merchant(self, user_id: int) -> bool:
        """Проверить, является ли пользователь мерчантом"""
        return self.user_manager.is_merchant(user_id)
    
    def is_admin(self, username: str) -> bool:
        """Проверить, является ли пользователь админом"""
        return self.user_manager.is_admin(username)
    
    def add_user(self, user_id: int, username: str, is_merchant: bool = False) -> bool:
        """Добавить пользователя"""
        return self.user_manager.add_user(user_id, username, is_merchant)
    
    def get_all_merchants(self) -> list:
        """Получить всех мерчантов"""
        return self.user_manager.get_all_merchants()
    
    def grant_merchant_access(self, user_id: int, shop_id: str, shop_api_key: str, order_id_tag: str = None) -> bool:
        """Предоставить доступ мерчанта"""
        return self.user_manager.grant_merchant_access(user_id, shop_id, shop_api_key, order_id_tag)
    
    def revoke_merchant_access(self, user_id: int) -> bool:
        """Отозвать доступ мерчанта"""
        return self.user_manager.revoke_merchant_access(user_id)
    
    def get_merchant_settings(self, user_id: int):
        """Получить настройки мерчанта"""
        return self.user_manager.get_merchant_settings(user_id)
    
    def get_info_content(self) -> str:
        """Получить содержимое информационного блока"""
        return self.info_manager.get_info_content()
    
    def update_info_content(self, content: str) -> bool:
        """Обновить содержимое информационного блока"""
        return self.info_manager.update_info_content(content)
    
    def get_next_order_id(self, user_id: int) -> str:
        """Получить следующий ID заказа"""
        return self.order_manager.get_next_order_id(user_id)
    
    def delete_user(self, username: str) -> bool:
        """Удалить пользователя"""
        return self.user_manager.delete_user(username)
    
    def get_all_users(self) -> list:
        """Получить всех пользователей"""
        query = "SELECT user_id, username FROM users"
        return self.db_manager.execute_query(query)

# Создаем глобальный экземпляр бота
bot_instance = MerchantBot()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    username = user.username
    
    # Добавляем пользователя в базу данных
    bot_instance.add_user(user.id, username)
    
    if bot_instance.is_merchant(user.id):
        # Мерчант
        message = Messages.WELCOME_MERCHANT.format(username=username)
        reply_markup = bot_instance.keyboard_manager.get_merchant_main_menu()
        await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        # Обычный пользователь
        message = Messages.WELCOME_REGULAR.format(username=username)
        await update.message.reply_text(message)

async def infoedit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для редактирования информационного блока (только для админов)"""
    user = update.effective_user
    username = user.username
    
    if not bot_instance.is_admin(username):
        await update.message.reply_text(Messages.ERROR_NOT_ADMIN)
        return
    
    # Устанавливаем состояние ожидания ввода нового содержимого
    context.user_data['current_state'] = UserState.WAITING_FOR_INFO_EDIT.value
    await update.message.reply_text("📝 Введите новое содержимое информационного блока:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений"""
    user = update.effective_user
    message_text = update.message.text
    
    # Приоритетная обработка кнопки "Главное меню"
    if message_text == Buttons.MAIN_MENU:
        StateManager.clear_all_states(context)
        
        if bot_instance.is_merchant(user.id):
            reply_markup = bot_instance.keyboard_manager.get_merchant_main_menu()
            await update.message.reply_text(Messages.WELCOME_MERCHANT.format(username=user.username), reply_markup=reply_markup)
        elif bot_instance.is_admin(user.username):
            reply_markup = bot_instance.keyboard_manager.get_admin_main_menu()
            await update.message.reply_text(Messages.ADMIN_WELCOME, reply_markup=reply_markup)
        else:
            await update.message.reply_text(Messages.WELCOME_REGULAR.format(username=user.username))
        return
    
    # Обработка через обработчики сообщений
    if await bot_instance.message_handlers.handle_message(update, context):
        return
    
    # Если сообщение не обработано, показываем соответствующее меню
    if bot_instance.is_merchant(user.id):
        reply_markup = bot_instance.keyboard_manager.get_merchant_main_menu()
        await update.message.reply_text("Выберите действие из меню:", reply_markup=reply_markup)
    elif bot_instance.is_admin(user.username):
        reply_markup = bot_instance.keyboard_manager.get_admin_main_menu()
        await update.message.reply_text("Выберите действие из меню:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback запросов"""
    query = update.callback_query
    await query.answer()
    
    # Обработка через обработчики callback
    await bot_instance.callback_handlers.handle_callback(update, context)

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("infoedit", infoedit_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()