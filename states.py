"""
Состояния пользователя для многошаговых операций
"""
from enum import Enum

class UserState(Enum):
    """Состояния пользователя"""
    # Состояния создания инвойса
    WAITING_FOR_INVOICE_ID = "waiting_for_invoice_id"
    WAITING_FOR_CLIENT_ID = "waiting_for_client_id"
    WAITING_FOR_AMOUNT = "waiting_for_amount"
    
    # Состояния создания выплаты
    WAITING_FOR_PAYOUT_ORDER_ID = "waiting_for_payout_order_id"
    WAITING_FOR_PAYOUT_CLIENT_ID = "waiting_for_payout_client_id"
    WAITING_FOR_IBAN_ACCOUNT = "waiting_for_iban_account"
    WAITING_FOR_IBAN_INN = "waiting_for_iban_inn"
    WAITING_FOR_SURNAME = "waiting_for_surname"
    WAITING_FOR_NAME = "waiting_for_name"
    WAITING_FOR_MIDDLENAME = "waiting_for_middlename"
    WAITING_FOR_PURPOSE = "waiting_for_purpose"
    WAITING_FOR_PAYOUT_AMOUNT = "waiting_for_payout_amount"
    
    # Состояния админа
    WAITING_FOR_ADMIN_USERNAME = "waiting_for_admin_username"
    WAITING_FOR_ADMIN_SHOP_ID = "waiting_for_admin_shop_id"
    WAITING_FOR_ADMIN_API_KEY = "waiting_for_admin_api_key"
    WAITING_FOR_ADMIN_ORDER_TAG = "waiting_for_admin_order_tag"
    WAITING_FOR_ADMIN_DELETE_USERNAME = "waiting_for_admin_delete_username"
    WAITING_FOR_ADMIN_DELETE_SHOP_ID = "waiting_for_admin_delete_shop_id"
    WAITING_FOR_ADMIN_BROADCAST = "waiting_for_admin_broadcast"
    WAITING_FOR_INFO_EDIT = "waiting_for_info_edit"
    
    # Состояния выхода
    WAITING_FOR_LOGOUT_CONFIRMATION = "waiting_for_logout_confirmation"

class StateManager:
    """Менеджер состояний пользователя"""
    
    @staticmethod
    def clear_invoice_states(context):
        """Очистка состояний создания инвойса"""
        states_to_clear = [
            'invoice_order_id', 'invoice_client_id', 'invoice_amount',
            UserState.WAITING_FOR_INVOICE_ID.value,
            UserState.WAITING_FOR_CLIENT_ID.value,
            UserState.WAITING_FOR_AMOUNT.value
        ]
        for state in states_to_clear:
            context.user_data.pop(state, None)
    
    @staticmethod
    def clear_payout_states(context):
        """Очистка состояний создания выплаты"""
        states_to_clear = [
            'payout_order_id', 'payout_client_id', 'payout_iban_account',
            'payout_iban_inn', 'payout_surname', 'payout_name', 'payout_middlename',
            'payout_purpose', 'payout_amount',
            UserState.WAITING_FOR_PAYOUT_ORDER_ID.value,
            UserState.WAITING_FOR_PAYOUT_CLIENT_ID.value,
            UserState.WAITING_FOR_IBAN_ACCOUNT.value,
            UserState.WAITING_FOR_IBAN_INN.value,
            UserState.WAITING_FOR_SURNAME.value,
            UserState.WAITING_FOR_NAME.value,
            UserState.WAITING_FOR_MIDDLENAME.value,
            UserState.WAITING_FOR_PURPOSE.value,
            UserState.WAITING_FOR_PAYOUT_AMOUNT.value
        ]
        for state in states_to_clear:
            context.user_data.pop(state, None)
    
    @staticmethod
    def clear_admin_states(context):
        """Очистка состояний админа"""
        states_to_clear = [
            'temp_username', 'temp_shop_id', 'temp_shop_api_key', 'temp_order_id_tag',
            'delete_username',
            UserState.WAITING_FOR_ADMIN_USERNAME.value,
            UserState.WAITING_FOR_ADMIN_SHOP_ID.value,
            UserState.WAITING_FOR_ADMIN_API_KEY.value,
            UserState.WAITING_FOR_ADMIN_ORDER_TAG.value,
            UserState.WAITING_FOR_ADMIN_DELETE_USERNAME.value,
            UserState.WAITING_FOR_ADMIN_DELETE_SHOP_ID.value,
            UserState.WAITING_FOR_INFO_EDIT.value,
            UserState.WAITING_FOR_ADMIN_BROADCAST.value
        ]
        for state in states_to_clear:
            context.user_data.pop(state, None)
    
    @staticmethod
    def clear_logout_states(context):
        """Очистка состояний выхода"""
        context.user_data.pop(UserState.WAITING_FOR_LOGOUT_CONFIRMATION.value, None)
    
    @staticmethod
    def clear_all_states(context):
        """Очистка всех состояний"""
        StateManager.clear_invoice_states(context)
        StateManager.clear_payout_states(context)
        StateManager.clear_admin_states(context)
        StateManager.clear_logout_states(context)
