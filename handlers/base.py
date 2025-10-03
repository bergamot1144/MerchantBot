"""
Базовые классы для обработчиков команд и состояний
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


class BaseHandler(ABC):
    """Базовый класс для всех обработчиков"""
    
    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Обрабатывает входящее сообщение
        
        Returns:
            bool: True если сообщение было обработано, False иначе
        """
        pass


class BaseCommand(BaseHandler):
    """Базовый класс для команд"""
    
    def __init__(self, command_name: str):
        self.command_name = command_name
    
    def can_handle(self, message_text: str) -> bool:
        """Проверяет, может ли команда обработать данное сообщение"""
        return message_text == self.command_name


class BaseState(BaseHandler):
    """Базовый класс для состояний"""
    
    def __init__(self, state_name: str):
        self.state_name = state_name
    
    def can_handle(self, user_data: Dict[str, Any]) -> bool:
        """Проверяет, может ли состояние обработать данные пользователя"""
        return user_data.get('current_state') == self.state_name
    
    def set_state(self, context: ContextTypes.DEFAULT_TYPE, next_state: Optional[str] = None):
        """Устанавливает следующее состояние"""
        if next_state:
            context.user_data['current_state'] = next_state
        else:
            context.user_data.pop('current_state', None)
    
    def clear_state_data(self, context: ContextTypes.DEFAULT_TYPE):
        """Очищает данные состояния"""
        keys_to_remove = [key for key in context.user_data.keys() if key.startswith('state_')]
        for key in keys_to_remove:
            context.user_data.pop(key, None)
