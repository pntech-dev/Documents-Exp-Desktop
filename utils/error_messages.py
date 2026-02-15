import requests

def get_friendly_error_message(exception: Exception) -> str:
    """
    Translates exceptions into user-friendly Russian messages.

    Args:
        exception (Exception): The exception to translate.

    Returns:
        str: A user-friendly error message.
    """
    
    if isinstance(exception, requests.exceptions.ConnectionError):
        return "Не удалось подключиться к серверу. Проверьте соединение или попробуйте позже."
    
    if isinstance(exception, requests.exceptions.Timeout):
        return "Превышено время ожидания ответа от сервера."

    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response is not None:
            status_code = exception.response.status_code
            
            # Try to get detail from JSON response
            try:
                detail = exception.response.json().get("detail")
            except:
                detail = None

            if status_code == 400:
                return f"Ошибка запроса: {detail}" if detail else "Некорректный запрос."
            
            if status_code == 401:
                return "Ошибка авторизации. Сессия истекла или данные неверны."
            
            if status_code == 403:
                return f"Доступ запрещен: {detail}" if detail else "У вас нет прав для этого действия."
            
            if status_code == 404:
                return f"Не найдено: {detail}" if detail else "Запрашиваемый ресурс не найден."
            
            if status_code == 409:
                return f"Конфликт: {detail}" if detail else "Конфликт данных (возможно, такая запись уже существует)."
            
            if status_code == 422:
                return f"Ошибка валидации: {detail}" if detail else "Ошибка проверки данных."

            if status_code == 429:
                return "Слишком много попыток. Пожалуйста, подождите 60 секунд."
            
            if status_code >= 500:
                return f"Внутренняя ошибка сервера ({status_code}). Попробуйте позже."
    
    return str(exception)
