from enum import Enum


class OperatorSwitchText(Enum):
    rus = "Ожидайте, соединяю вас с оператором"


class TranscribedTextFailed(Enum):
    rus = "Не удалось расшифровать голосовое сообщение."


class WaitingMessage(Enum):
    rus = "⏳"


class ImageProcessingFailed(Enum):
    rus = "⚠️ Не удалось обработать изображение. Пожалуйста, повторите запрос в другом формате."


class DocumentImageProcessingFailed(Enum):
    rus = "⚠️ Не удалось обработать изображение из файла. Пожалуйста, повторите запрос в другом формате."


class UnsupportedMessageType(Enum):
    rus = "⚠️ Данный тип сообщений не поддерживается. Пожалуйста, отправьте текст, голосовое сообщение или изображение."


class InternalError(Enum):
    rus = "Internal error. Please try again."
