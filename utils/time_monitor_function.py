import time


def timed(wrapped_fun):
    def inner(*args, **kwargs):
        t1 = time.process_time()
        ret = wrapped_fun(*args, **kwargs)
        print(f"function = {wrapped_fun.__name__}")
        print(f"process time = {time.process_time() - t1}")
        return ret

    return inner
