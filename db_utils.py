"""Утилиты для работы с базой данных MongoDB."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from config import MONGO_DB_NAME, MONGO_URI

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер соединений с MongoDB."""

    def __init__(self, mongo_uri: str = MONGO_URI, db_name: str = MONGO_DB_NAME):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_collection(self, name: str) -> Collection:
        """Возвращает коллекцию MongoDB по имени."""

        return self.db[name]


class UserManager:
    """Менеджер для работы с пользователями."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.users = self.db.get_collection("users")
        self.merchant_settings = self.db.get_collection("merchant_settings")

    @staticmethod
    def _normalize_username(username: Optional[str]) -> Optional[str]:
        if not username:
            return None
        return username.replace("@", "").strip()

    def _get_user_filter(self, identifier: Union[int, str]) -> Dict[str, Any]:
        if isinstance(identifier, int):
            return {"user_id": identifier}
        normalized = self._normalize_username(identifier)
        if not normalized:
            return {"username": None}
        return {"$or": [{"_id": normalized}, {"username": normalized}]}

    def is_merchant(self, user_id: int) -> bool:
        """Проверить, является ли пользователь мерчантом."""

        user = self.users.find_one({"user_id": user_id})
        return bool(user and user.get("is_merchant"))

    def is_admin(self, username: str) -> bool:
        """Проверить, является ли пользователь админом."""

        from config import ADMIN_USERNAME

        return username == ADMIN_USERNAME

    def add_user(self, user_id: int, username: str, is_merchant: bool = False) -> bool:
        """Добавить пользователя или обновить существующего."""

        normalized_username = self._normalize_username(username)
        now = datetime.utcnow()

        try:
            existing = self.users.find_one({"user_id": user_id})
            if not existing and normalized_username:
                existing = self.users.find_one({"_id": normalized_username})

            if existing:
                update_fields: Dict[str, Any] = {
                    "user_id": user_id,
                    "username": normalized_username or existing.get("username"),
                }
                if is_merchant:
                    update_fields["is_merchant"] = True
                self.users.update_one({"_id": existing["_id"]}, {"$set": update_fields})
                user_key = existing["_id"]
            else:
                user_key = normalized_username or str(user_id)
                document: Dict[str, Any] = {
                    "_id": user_key,
                    "user_id": user_id,
                    "username": normalized_username or str(user_id),
                    "is_merchant": is_merchant,
                    "created_at": now,
                }
                self.users.insert_one(document)

            # Обновляем связанные настройки мерчанта с новым user_id
            self.merchant_settings.update_one(
                {"_id": user_key},
                {"$set": {"user_id": user_id}},
                upsert=False,
            )

            return True
        except PyMongoError as exc:
            logger.error("Ошибка добавления пользователя: %s", exc)
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей с настройками мерчанта."""

        pipeline = [
            {
                "$lookup": {
                    "from": "merchant_settings",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "settings",
                }
            },
            {"$unwind": {"path": "$settings", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"created_at": -1, "username": 1}},
        ]

        users: List[Dict[str, Any]] = []
        for document in self.users.aggregate(pipeline):
            settings = document.get("settings") or {}
            users.append(
                {
                    "user_id": document.get("user_id"),
                    "username": document.get("username"),
                    "first_name": document.get("first_name"),
                    "last_name": document.get("last_name"),
                    "is_merchant": document.get("is_merchant", False),
                    "shop_id": settings.get("shop_id"),
                    "shop_api_key": settings.get("shop_api_key"),
                    "order_id_tag": settings.get("order_id_tag"),
                    "created_at": document.get("created_at"),
                }
            )

        return users

    def get_all_merchants(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей-мерчантов."""

        return [user for user in self.get_all_users() if user.get("is_merchant")]

    def grant_merchant_access(
        self,
        identifier: Union[int, str],
        shop_id: str,
        shop_api_key: str,
        order_id_tag: Optional[str] = None,
    ) -> bool:
        """Предоставить доступ мерчанта."""

        filter_query = self._get_user_filter(identifier)

        try:
            user = self.users.find_one(filter_query)

            if not user:
                if isinstance(identifier, int):
                    logger.error("Не удалось найти пользователя с user_id=%s для выдачи доступа", identifier)
                    return False

                normalized_username = self._normalize_username(str(identifier))
                if not normalized_username:
                    return False

                now = datetime.utcnow()
                user_document: Dict[str, Any] = {
                    "_id": normalized_username,
                    "username": normalized_username,
                    "is_merchant": True,
                    "created_at": now,
                }
                self.users.insert_one(user_document)
                user_key = normalized_username
            else:
                user_key = user["_id"]
                update_fields: Dict[str, Any] = {"is_merchant": True}
                if isinstance(identifier, int):
                    update_fields["user_id"] = identifier
                self.users.update_one({"_id": user_key}, {"$set": update_fields})

            settings_update = {
                "shop_id": shop_id,
                "shop_api_key": shop_api_key,
                "order_id_tag": order_id_tag,
            }
            if isinstance(identifier, int):
                settings_update["user_id"] = identifier
            elif user and user.get("user_id"):
                settings_update["user_id"] = user.get("user_id")

            self.merchant_settings.update_one(
                {"_id": user_key},
                {"$set": settings_update},
                upsert=True,
            )

            return True
        except PyMongoError as exc:
            logger.error("Ошибка предоставления доступа мерчанта: %s", exc)
            return False

    def revoke_merchant_access(self, user_id: int) -> bool:
        """Отозвать доступ мерчанта."""

        try:
            user = self.users.find_one({"user_id": user_id})
            if not user:
                return False

            self.users.update_one({"_id": user["_id"]}, {"$set": {"is_merchant": False}})
            self.merchant_settings.delete_one({"_id": user["_id"]})
            return True
        except PyMongoError as exc:
            logger.error("Ошибка отзыва доступа мерчанта: %s", exc)
            return False

    def get_merchant_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить настройки мерчанта."""

        user = self.users.find_one({"user_id": user_id})
        if not user:
            return None

        return self.merchant_settings.find_one({"_id": user["_id"]})

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе по username."""

        normalized_username = self._normalize_username(username)
        if not normalized_username:
            return None

        user = self.users.find_one({"$or": [{"_id": normalized_username}, {"username": normalized_username}]})
        if not user:
            return None

        settings = self.merchant_settings.find_one({"_id": user["_id"]}) or {}
        return {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "is_merchant": user.get("is_merchant", False),
            "shop_id": settings.get("shop_id"),
            "shop_api_key": settings.get("shop_api_key"),
            "order_id_tag": settings.get("order_id_tag"),
            "created_at": user.get("created_at"),
        }

    def delete_user(self, username: str) -> bool:
        """Удалить пользователя."""

        normalized_username = self._normalize_username(username)
        if not normalized_username:
            return False

        user = self.users.find_one({"$or": [{"_id": normalized_username}, {"username": normalized_username}]})
        if not user:
            return False

        user_key = user["_id"]

        try:
            result = self.users.delete_one({"_id": user_key})
            self.merchant_settings.delete_one({"_id": user_key})
            return result.deleted_count > 0
        except PyMongoError as exc:
            logger.error("Ошибка удаления пользователя: %s", exc)
            return False


class InfoManager:
    """Менеджер для работы с информационным блоком."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collection = self.db.get_collection("info_block")

    def get_info_content(self) -> str:
        """Получить содержимое информационного блока."""

        document = self.collection.find_one({"_id": 1})
        return document.get("content") if document else "Информационный блок не настроен."

    def update_info_content(self, content: str) -> bool:
        """Обновить содержимое информационного блока."""

        try:
            self.collection.update_one({"_id": 1}, {"$set": {"content": content}}, upsert=True)
            return True
        except PyMongoError as exc:
            logger.error("Ошибка обновления информационного блока: %s", exc)
            return False


class OrderManager:
    """Менеджер для работы с заказами."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.merchant_settings = self.db.get_collection("merchant_settings")
        self.order_counters = self.db.get_collection("order_counters")

    def get_next_order_id(self, user_id: int) -> str:
        """Получить следующий ID заказа."""

        settings = self.merchant_settings.find_one({"user_id": user_id})
        order_id_tag = settings.get("order_id_tag") if settings and settings.get("order_id_tag") else "ManagerApple"

        counter_doc = self.order_counters.find_one_and_update(
            {"order_id_tag": order_id_tag},
            {"$inc": {"counter": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        counter = counter_doc.get("counter", 1)
        return f"{order_id_tag}_{counter}"
