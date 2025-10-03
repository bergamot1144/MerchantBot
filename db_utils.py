"""
Утилиты для работы с базой данных
"""
import sqlite3
import logging
from typing import Optional, List, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Выполнить запрос и вернуть результат"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Выполнить обновление и вернуть успешность"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            return False
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Выполнить множественный запрос"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка выполнения множественного запроса: {e}")
            return False

class UserManager:
    """Менеджер для работы с пользователями"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def is_merchant(self, user_id: int) -> bool:
        """Проверить, является ли пользователь мерчантом"""
        query = "SELECT is_merchant FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,))
        return result[0][0] if result else False
    
    def is_admin(self, username: str) -> bool:
        """Проверить, является ли пользователь админом"""
        from config import ADMIN_USERNAME
        return username == ADMIN_USERNAME
    
    def add_user(self, user_id: int, username: str, is_merchant: bool = False) -> bool:
        """Добавить пользователя"""
        query = """
            INSERT OR IGNORE INTO users (user_id, username, is_merchant) 
            VALUES (?, ?, ?)
        """
        return self.db.execute_update(query, (user_id, username, is_merchant))
    
    def get_all_merchants(self) -> List[Tuple]:
        """Получить всех мерчантов"""
        query = """
            SELECT u.user_id, u.username, ms.shop_id, ms.shop_api_key, ms.order_id_tag
            FROM users u
            LEFT JOIN merchant_settings ms ON u.user_id = ms.user_id
            WHERE u.is_merchant = TRUE
        """
        return self.db.execute_query(query)
    
    def grant_merchant_access(self, user_id: int, shop_id: str, shop_api_key: str, order_id_tag: str = None) -> bool:
        """Предоставить доступ мерчанта"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Обновляем статус пользователя
                cursor.execute('''
                    UPDATE users SET is_merchant = TRUE WHERE user_id = ?
                ''', (user_id,))
                
                # Добавляем или обновляем настройки мерчанта
                cursor.execute('''
                    INSERT OR REPLACE INTO merchant_settings (user_id, shop_id, shop_api_key, order_id_tag)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, shop_id, shop_api_key, order_id_tag))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка предоставления доступа мерчанта: {e}")
            return False
    
    def revoke_merchant_access(self, user_id: int) -> bool:
        """Отозвать доступ мерчанта"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Удаляем настройки мерчанта
                cursor.execute('DELETE FROM merchant_settings WHERE user_id = ?', (user_id,))
                # Обновляем статус пользователя
                cursor.execute('UPDATE users SET is_merchant = FALSE WHERE user_id = ?', (user_id,))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка отзыва доступа мерчанта: {e}")
            return False
    
    def get_merchant_settings(self, user_id: int) -> Optional[Tuple]:
        """Получить настройки мерчанта"""
        query = "SELECT user_id, shop_id, shop_api_key, order_id_tag FROM merchant_settings WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def delete_user(self, username: str) -> bool:
        """Удалить пользователя"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Получаем user_id
                cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                user_id = result[0]
                
                # Удаляем настройки мерчанта
                cursor.execute("DELETE FROM merchant_settings WHERE user_id = ?", (user_id,))
                # Удаляем пользователя
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя: {e}")
            return False

class InfoManager:
    """Менеджер для работы с информационным блоком"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_info_content(self) -> str:
        """Получить содержимое информационного блока"""
        query = "SELECT content FROM info_block WHERE id = 1"
        result = self.db.execute_query(query)
        return result[0][0] if result else "Информационный блок не настроен."
    
    def update_info_content(self, content: str) -> bool:
        """Обновить содержимое информационного блока"""
        query = "INSERT OR REPLACE INTO info_block (id, content) VALUES (1, ?)"
        return self.db.execute_update(query, (content,))

class OrderManager:
    """Менеджер для работы с заказами"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_next_order_id(self, user_id: int) -> str:
        """Получить следующий ID заказа"""
        # Получаем order_id_tag пользователя
        query = "SELECT order_id_tag FROM merchant_settings WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,))
        
        if result and result[0][0]:
            order_id_tag = result[0][0]
        else:
            order_id_tag = "ManagerApple"
        
        # Получаем текущий счетчик
        query = "SELECT counter FROM order_counters WHERE order_id_tag = ?"
        result = self.db.execute_query(query, (order_id_tag,))
        
        if result:
            counter = result[0][0] + 1
            # Обновляем счетчик
            query = "UPDATE order_counters SET counter = ? WHERE order_id_tag = ?"
            self.db.execute_update(query, (counter, order_id_tag))
        else:
            counter = 1
            # Создаем новый счетчик
            query = "INSERT INTO order_counters (order_id_tag, counter) VALUES (?, ?)"
            self.db.execute_update(query, (order_id_tag, counter))
        
        return f"{order_id_tag}_{counter}"
