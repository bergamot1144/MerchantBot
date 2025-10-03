# MerchantBot - Telegram Bot для мерчантов Konver2pay

Рефакторенная версия Telegram бота для управления инвойсами и выплатами на платформе Konver2pay.

## 🏗️ Архитектура

Проект использует современные паттерны проектирования для лучшей организации кода:

### Структура проекта:

```
📁 handlers/
├── __init__.py              # Инициализация пакета
├── base.py                  # Базовые классы (BaseHandler, BaseCommand, BaseState)
├── admin_commands.py        # Команды администратора
├── merchant_commands.py     # Команды мерчанта
├── states.py               # Обработчики состояний пользователей
└── command_dispatcher.py   # Диспетчер команд

📄 MerchantBot.py           # Основной файл бота
📄 config.py                # Конфигурация
📄 requirements.txt         # Зависимости Python
📄 setup_db_with_test_user.py # Скрипт инициализации БД
🗃️ db.db                   # База данных SQLite
```

### Использованные паттерны:

- **Command Pattern** - каждая команда это отдельный класс
- **State Machine** - управление состояниями пользователей
- **Strategy Pattern** - разные обработчики для разных типов сообщений
- **Dispatcher Pattern** - централизованная обработка команд

## 🚀 Установка и запуск

### 1. Клонирование и настройка окружения:

```bash
# Активация виртуального окружения
.\merchBotEnv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации:

Отредактируйте `config.py`:

```python
BOT_TOKEN = "ваш_токен_бота"
ADMIN_USERNAME = "ваш_username"
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "merchant_bot"
```

### 3. Запуск MongoDB

Убедитесь, что экземпляр MongoDB доступен по адресу, указанному в `MONGO_URI` (по умолчанию `mongodb://localhost:27017`).

### 4. Запуск бота:

```bash
python MerchantBot.py
```

## 👥 Функциональность

### Для администраторов:

- 👤 **Управление пользователями** - просмотр, добавление, удаление
- ✉️ **Рассылка сообщений** - отправка уведомлений всем пользователям
- 📄 **Редактирование информации** - команда `/infoedit`

### Для мерчантов:

- 👤 **Профиль** - просмотр данных аккаунта
- 📄 **Информация** - просмотр информационного блока
- 🎰 **Создание инвойсов** - Card, OneClick, IBAN
- 💎 **Создание выплат** - Card, IBAN
- ❌ **Выход из аккаунта** - с подтверждением username

## 🔧 Расширение функциональности

### Добавление новой команды:

```python
# В handlers/admin_commands.py или handlers/merchant_commands.py
class NewCommand(BaseCommand):
    def __init__(self, bot_instance):
        super().__init__("🆕 Новая команда")
        self.bot_instance = bot_instance

    async def handle(self, update, context):
        # Логика команды
        await update.message.reply_text("Новая команда выполнена!")
        return True

# В handlers/command_dispatcher.py добавить в _initialize_handlers():
self.commands.append(NewCommand(self.bot_instance))
```

### Добавление нового состояния:

```python
# В handlers/states.py
class NewState(BaseState):
    def __init__(self, bot_instance):
        super().__init__('new_state')
        self.bot_instance = bot_instance

    async def handle(self, update, context):
        # Логика состояния
        return True
```

## 📊 База данных

### Коллекции MongoDB:

- **users** — данные пользователей и их статусы
- **merchant_settings** — привязанные к пользователям shop_id, API-ключи и order_id_tag
- **info_block** — содержимое информационного блока
- **order_counters** — счетчики для генерации order_id

### Методы работы с БД:

- `add_user()` - добавление пользователя
- `grant_merchant_access()` - предоставление доступа мерчанта
- `revoke_merchant_access()` - отзыв доступа мерчанта
- `get_all_users()` - получение всех пользователей
- `delete_user()` - удаление пользователя

## 🎯 Преимущества рефакторинга

✅ **Нет бесконечных `elif`** - каждая команда в своем классе  
✅ **Легко добавлять новые команды** - просто создать новый класс  
✅ **Четкое разделение ответственности** - админ/мерчант/состояния  
✅ **Переиспользуемый код** - базовые классы для всех обработчиков  
✅ **Легкое тестирование** - каждый компонент изолирован  
✅ **Масштабируемость** - простое добавление новой функциональности

## 📝 Логирование

Бот использует стандартное логирование Python. Настройки в `config.py`:

```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🔒 Безопасность

- Проверка прав администратора по username
- Подтверждение удаления пользователей через shop_id
- Подтверждение выхода из аккаунта через username
- Валидация входных данных

## 📞 Поддержка

При возникновении проблем проверьте:

1. Правильность токена бота в `config.py`
2. Доступность MongoDB по адресу из `MONGO_URI`
3. Активность виртуального окружения
4. Установленные зависимости из `requirements.txt`
