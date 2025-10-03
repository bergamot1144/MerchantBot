"""
Константы для Telegram бота MerchantBot
"""

# Сообщения для пользователей
class Messages:
    # Приветствие
    WELCOME_MERCHANT = "Привет, @{username} 👋🏻\n\nДобро пожаловать в панель управления мерчанта Konver2pay!"
    WELCOME_REGULAR = "Привет, @{username} 👋🏻\n\nЭтот Бот поможет Мерчантам Платформы Konver2pay создавать инвойсы и выплаты.\n\nЧтобы получить доступ к функционалу, обратитесь к Администратору."
    
    # Профиль
    PROFILE_TITLE = "👤 Профиль"
    PROFILE_FORMAT = "• Username: @{username}\n• Shop ID: {shop_id}\n• Shop API Key: {shop_api_key}\n• Order ID Tag: {order_id_tag}"
    PROFILE_NO_DATA = "👤 Профиль\n\n• Username: @{username}\n\nДанные мерчанта не найдены."
    
    # Информация
    INFO_TITLE = "📄 Информация"
    
    # Инвойсы
    INVOICE_METHOD_SELECTION = "🎰 Выберите метод для инвойса"
    INVOICE_ID_INPUT = "🎰 Укажите ID инвойса"
    INVOICE_CLIENT_ID_INPUT = "🎰 Укажите ID Клиента"
    INVOICE_AMOUNT_INPUT = "🎰 Укажите сумму"
    INVOICE_CONFIRMATION = "🎰 Заявка на инвойс\n\n• ID инвойса: {order_id}\n• ID Клиента: {client_id}\n• Сумма: {amount} UAH"
    INVOICE_SUCCESS = "✅ Успех\nИнвойс был создан.\n\n• ID ордера: {invoice_id}\n• ID инвойса: {order_id}\n• ID Клиента: {client_id}\n• Сумма: {amount} UAH\n\nСсылка на платежное окно: {pay_url}"
    INVOICE_ERROR = "⚠️ Ошибка\nИнвойс не был создан. Проверьте данные заявки и попробуйте ещё раз.\n\nКод ошибки: {error_code}\nСтатус: {error_message}"
    
    # Выплаты
    PAYOUT_METHOD_SELECTION = "💎 Выберите метод для выплаты"
    PAYOUT_ORDER_ID_INPUT = "💎 Укажите ID заявки"
    PAYOUT_CLIENT_ID_INPUT = "💎 Укажите ID Клиента"
    PAYOUT_IBAN_INPUT = "💎 Укажите IBAN-счет Клиента"
    PAYOUT_INN_INPUT = "💎 Укажите ИНН Клиента"
    PAYOUT_SURNAME_INPUT = "💎 Укажите фамилию Клиента"
    PAYOUT_NAME_INPUT = "💎 Укажите имя Клиента"
    PAYOUT_MIDDLENAME_INPUT = "💎 Укажите отчество Клиента"
    PAYOUT_PURPOSE_INPUT = "💎 Укажите назначение платежа Клиента"
    PAYOUT_AMOUNT_INPUT = "💎 Укажите сумму"
    PAYOUT_CONFIRMATION = "💎 Заявка на выплату\n\n• ID заявки: {order_id}\n• ID Клиента: {client_id}\n• Номер iBAN-счета: {iban_account}\n• ИНН: {iban_inn}\n• ФИО: {full_name}\n• Назначение платежа: {purpose}\n• Сумма: {amount} UAH"
    PAYOUT_SUCCESS = "✅ Успех\nВыплата была создана.\n\n• ID выплаты: {withdrawal_id}\n• ID заявки: {order_id}\n• ID Клиента: {client_id}\n• Номер iBAN-счета: {iban_account}\n• ИНН: {iban_inn}\n• ФИО: {full_name}\n• Назначение платежа: {purpose}\n• Сумма: {amount} UAH"
    PAYOUT_ERROR = "⚠️ Ошибка\nВыплата не была создана. Проверьте данные заявки и попробуйте ещё раз.\n\nКод ошибки: {error_code}\nСтатус: {error_message}"
    
    # Выход из аккаунта
    LOGOUT_CONFIRMATION = "❌ Вы действительно хотите отвязать свой аккаунт от Бота?\n\nЧтобы подтвердить действие, отправьте свой @username в следующем сообщении."
    LOGOUT_SUCCESS = "✅ Аккаунт успешно отвязан от бота."
    
    # Админка
    ADMIN_WELCOME = "👨🏻‍💻 Панель администратора\n\nВыберите действие:"
    ADMIN_USERS_LIST = "👤 Пользователи, у которых есть доступ к Боту:"
    ADMIN_USER_FORMAT = "{index}) @{username} shop_id: {shop_id} shop_api_key: {shop_api_key}"
    ADMIN_BROADCAST_INPUT = "✉️ Введите текст рассылки:"
    ADMIN_BROADCAST_SUCCESS = "✅ Рассылка отправлена {count} пользователям."
    ADMIN_ADD_USER_USERNAME = "👤 Введите @username пользователя:"
    ADMIN_ADD_USER_SHOP_ID = "👤 Введите shop_id:"
    ADMIN_ADD_USER_API_KEY = "👤 Введите shop_api_key:"
    ADMIN_ADD_USER_ORDER_TAG = "👤 Укажите значение, которое будет привязано к этому Telegram-аккаунту, как ORDER ID TAG при создании инвойса или выплаты."
    ADMIN_ADD_USER_SUCCESS = "✅ Пользователь @{username} успешно добавлен с доступом к функционалу мерчанта."
    ADMIN_DELETE_USER_USERNAME = "❌ Введите @username пользователя для удаления:"
    ADMIN_DELETE_USER_SHOP_ID = "❌ Для подтверждения действия отправьте shop_id, к которому был привязан пользователь @{username}."
    ADMIN_DELETE_USER_ERROR = "⚠️ Ошибка\nПодтвердить удаление пользователя не удалось. Указанный shop_id не привязан к заявленному username."
    ADMIN_DELETE_USER_SUCCESS = "❌ Пользователь успешно удален"
    
    # Ошибки
    ERROR_MERCHANT_NOT_FOUND = "❌ Ошибка: Настройки мерчанта не найдены."
    ERROR_NOT_MERCHANT = "❌ У вас нет доступа к этому функционалу."
    ERROR_NOT_ADMIN = "❌ У вас нет прав администратора."

# Кнопки
class Buttons:
    # Главное меню мерчанта
    PROFILE = "👤 Профиль"
    INFO = "📄 Информация"
    CREATE_INVOICE = "🎰 Создать инвойс"
    CREATE_PAYOUT = "💎 Создать выплату"
    LOGOUT = "❌ Выйти из аккаунта"
    MAIN_MENU = "◀️ Главное меню"
    
    # Админка
    USERS = "👤 Пользователи"
    BROADCAST = "✉️ Создать рассылку"
    ADD_USER = "👤 Добавить пользователя"
    DELETE_USER = "❌ Удалить пользователя"
    
    # Инвойсы
    INVOICE_CARD = "💳 Card"
    INVOICE_ONECLICK = "⚡ OneClick"
    INVOICE_IBAN = "🏦 IBAN"
    
    # Выплаты
    PAYOUT_CARD = "💳 Card"
    PAYOUT_IBAN = "🏦 IBAN"
    
    # Подтверждение
    CONFIRM = "✅ Подтвердить"
    CANCEL = "❌ Отмена"
    SKIP = "Пропустить"
    
    # Назначения платежей
    PURPOSE_POPOVNENNYA = "Поповнення рахунку"
    PURPOSE_POVORENNYA = "Повернення боргу"
    PURPOSE_PEREKAZ = "Переказ коштів"

# Callback данные
class CallbackData:
    # Инвойсы
    INVOICE_METHOD_CARD = "invoice_method_card"
    INVOICE_METHOD_ONECLICK = "invoice_method_oneclick"
    INVOICE_METHOD_IBAN = "invoice_method_iban"
    INVOICE_CONFIRM = "invoice_confirm"
    INVOICE_CANCEL = "invoice_cancel"
    
    # Выплаты
    PAYOUT_METHOD_CARD = "payout_method_card"
    PAYOUT_METHOD_IBAN = "payout_method_iban"
    PAYOUT_PURPOSE_POPOVNENNYA = "purpose_popovnennya"
    PAYOUT_PURPOSE_POVORENNYA = "purpose_povorennya"
    PAYOUT_PURPOSE_PEREKAZ = "purpose_perekaz"
    PAYOUT_CONFIRM = "payout_confirm"
    PAYOUT_CANCEL = "payout_cancel"
    
    # Выход
    LOGOUT_CANCEL = "logout_cancel"
    
    # Админка
    ADMIN_BACK = "admin_back"
    ADMIN_SKIP = "admin_skip"
