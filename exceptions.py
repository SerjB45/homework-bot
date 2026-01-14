class TokenNotFound(Exception):
    """Исключение при проверке переменных окружения."""

    def __init__(self, message=''):  # noqa: D107
        self.message = message

    def __str__(self):  # noqa: D105
        return f'Отсутствует переменная окружения. {self.message}'


class MessageNotSend(Exception):
    """Сообщение не отправлено."""

    def __init__(self, message=''):  # noqa: D107
        self.message = message

    def __str__(self):  # noqa: D105
        return f'Возникла ошибка при отправке сообщения. {self.message}'


class UnknowStatusHomework(Exception):
    """Неизвестный статус домашней работы."""

    def __str__(self):  # noqa: D105
        return 'Неизвестный статус домашней работы.'
