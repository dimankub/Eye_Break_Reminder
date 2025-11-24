"""Базовый класс для notifier'ов"""
from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    """Базовый класс для всех notifier'ов"""
    
    @abstractmethod
    def notify(self, msg: str) -> None:
        """
        Отправляет уведомление
        
        Args:
            msg: Текст уведомления
        """
        pass
