class EnvVariableNotFound(Exception):
    """Исключение при проверке переменных окружения."""

    def __init__(self, message=''):  # noqa: D107
        self.message = message

    def __str__(self):  # noqa: D105
        return f'Отсутствует переменная окружения: {self.message}. '


class TokenNotFound(EnvVariableNotFound):
    """Исключение при проверке токенов."""

    def __str__(self):  # noqa: D105
        message = super().__str__() + 'Проверьте токены!'
        return message


class ChatIDNotFound(EnvVariableNotFound):
    """Исключение при ID чата."""

    def __str__(self):  # noqa: D105
        message = super().__str__() + 'Проверьте ID чата!'
        return message


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


class HTTPRequestStatusError(Exception):
    """Ошибка по статусу ответа."""

    pass


class HomeworkError(Exception):
    """Ошибка в данных по домашней работе."""

    pass


class DateRequestError(Exception):
    """Ошибка по дате запроса."""

    def __str__(self):  # noqa: D105
        return 'Возникла ошибка при получении даты запроса.'


class HTTPRequestOthersError(Exception):
    """Прочие ошибки при выполнении запроса."""

    def __init__(self, error, status_code):  # noqa: D107
        self.error = error
        self.status_code = status_code

    def __str__(self):  # noqa: D105
        return (
            f'Ошибка при запросе к API: {self.error}.'
            f'Код ответа {self.status_code}'
        )
