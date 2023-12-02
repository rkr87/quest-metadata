from datetime import datetime
from re import sub


def to_snake(string: str) -> str:
    '''
    TODO
    '''
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                string.replace('-', ' '))).split()).lower()


def to_pascal(snake: str) -> str:
    """
    TODO
    """
    return "".join(x.capitalize() for x in snake.lower().split("_"))


def to_camel(snake: str) -> str:
    """
    TODO
    """
    return snake[0].lower() + to_pascal(snake)[1:]


def to_kebab(snake: str) -> str:
    """
    TODO
    """
    return '-'.join(word for word in snake.split('_'))


def to_iso(data_str: str, _format: str) -> str:
    '''
    TODO
    '''
    try:
        return datetime.strptime(data_str, _format).isoformat()
    except ValueError:
        return data_str
