# Конфигурация бота
# Замените YOUR_BOT_TOKEN_HERE на ваш токен от BotFather

BOT_TOKEN = "7608770565:AAGZCjP2IVBgAU4Jaiah7ZomxnZMuRYQb28"
ADMIN_USERNAME = "vv_vega"
DATABASE_PATH = "db.db"

# API URLs для Konvert2pay
API_BASE_URL = "https://konvert2pay.me/api/v1"
INVOICE_CREATE_URL = f"{API_BASE_URL}/invoice_create.ashx"
WITHDRAWAL_CREATE_URL = f"{API_BASE_URL}/withdrawal_create.ashx"

# Webhook URL для отправки уведомлений
WEBHOOK_URL = "http://webhook-paytoday.online/webhook"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
