from datetime import timedelta
import logging
from typing import Callable, Coroutine
import redis
from app.conf.config import settings
import inspect
import pickle


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
)


logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


async def cache(
    fn: Callable,
    key: str,
    ttl: int = 60 * 60 * 24,
    args: list = [],
    kwargs: dict = {},
):
    """
    Cache the result of a function

    Args:
        fn (Callable): The function to cache
        key (str): The key to cache the result under
        ttl (int): The time to live for the cache
        args (list): The arguments to pass to the function
        kwargs (dict): The keyword arguments to pass to the function

    Returns:
        Any: The result of the function
    """
    try:
        res = redis_client.get(key)
        if res:
            logging.info(f"Cache hit for {key}")
            return pickle.loads(res)
    except Exception as e:
        logging.error(f"Error getting cache for {key}: {e}")
        pass

    res = await fn(*args, **kwargs)
    try:
        logging.info(f"Cache miss for {key}")
        redis_client.set(key, pickle.dumps(res), ex=ttl)
    except Exception as e:
        logging.error(f"Error setting cache for {key}: {e}")
        pass

    return res


async def invalidate(key: str):
    """
    Invalidate the cache for a function

    Args:
        key (str): The key to invalidate the cache for

    Returns:
        None
    """
    try:
        redis_client.delete(key)
    except Exception as e:
        logging.error(f"Error deleting cache for {key}: {e}")
        pass


def invalidate_cache(invalidator_function: Coroutine | Callable):
    """
    Invalidate the cache for a function

    Args:
        invalidator_function (Coroutine | Callable): The function to invalidate the cache for

    Returns:
        Callable: The decorated function
    """

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            try:
                maybe_coro = invalidator_function(result)
            except TypeError:
                maybe_coro = invalidator_function()

            if inspect.isawaitable(maybe_coro):
                await maybe_coro

            return result

        return wrapper

    return decorator
