import requests


def _extract_http_detail(response) -> str | None:
    """Extracts API error detail from JSON response payload."""
    try:
        payload = response.json()
    except ValueError:
        return None

    detail = payload.get("detail") if isinstance(payload, dict) else payload
    if detail is None:
        return None
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "; ".join(str(item) for item in detail if item is not None) or None
    return str(detail)


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
            detail = _extract_http_detail(exception.response)

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

            if detail:
                return f"HTTP {status_code}: {detail}"
            return f"Ошибка запроса (HTTP {status_code})."
    
    return str(exception)
