import functools
import time


def timefunc(func):
    @functools.wraps(func)
    def time_this_function(*args, **kwargs):
        start_time = time.perf_counter_ns()
        func_return = func(*args, **kwargs)
        stop_time = time.perf_counter_ns()
        timediff = (stop_time - start_time)/10e9
        # print(f"{func.__name__}" + "-"*(20-len(func.__name__)) + f"time = {timediff*1000:0.2f}ms, fps = {1/timediff : 0.0f}")
        return timediff, func_return
    return time_this_function

def clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val