# app/utils/cache.py
import json
import hashlib
from functools import wraps
from app.core.redis_client import redis_client

def is_json_serializable(obj):
    """Check if an object can be serialized to JSON."""
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False

def cache(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Filter out non-serializable args (db sessions, SQLAlchemy models)
            safe_args = []
            for arg in args:
                if is_json_serializable(arg):
                    safe_args.append(arg)
                elif hasattr(arg, "__class__") and "sqlalchemy" in str(arg.__class__):
                    # Skip SQLAlchemy objects entirely
                    continue
                else:
                    # Convert to string for safe serialization
                    safe_args.append(str(arg))
            
            safe_kwargs = {}
            for key, value in kwargs.items():
                if is_json_serializable(value):
                    safe_kwargs[key] = value
                elif hasattr(value, "__class__") and "sqlalchemy" in str(value.__class__):
                    # Skip SQLAlchemy objects entirely
                    continue
                else:
                    safe_kwargs[key] = str(value)
            
            # Generate key
            key_data = {
                'func_name': func.__name__,
                'args': safe_args,
                'kwargs': safe_kwargs
            }
            key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
            
            cached = redis_client.get(key)
            if cached is not None:
                return cached
            
            result = await func(*args, **kwargs)
            redis_client.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator