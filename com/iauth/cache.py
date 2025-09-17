import hashlib
import pickle
import time

cache = {}


def is_obsolete(entry, duration):
    return time.time() - entry['time'] > duration


def compute_key(func, args, kw):
    key = pickle.dumps((func.__name__, args, kw))
    return hashlib.sha1(key).hexdigest()


def memorize(duration=10):
    def _memorize(func):
        def __memorize(*args, **kw):
            key = compute_key(func, args, kw)

            # if has it?
            if key in cache and not is_obsolete(cache[key], duration):
                print('we got from cache')
                return cache[key]['value']

            # store
            # print("store")
            result = func(*args, **kw)
            cache[key] = {'value': result, 'time': time.time()}
            return result

        return __memorize

    return _memorize
