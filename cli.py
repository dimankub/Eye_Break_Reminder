"""Модуль для парсинга аргументов командной строки"""
import argparse

def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки
    
    Returns:
        Объект Namespace с аргументами
    """
    parser = argparse.ArgumentParser(description='EyeCare Reminder - напоминания для здоровья глаз')
    parser.add_argument('--lang', type=str, help='Язык интерфейса (ru, en, auto)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование (DEBUG уровень)')
    return parser.parse_args()

