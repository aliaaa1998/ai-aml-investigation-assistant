from time import perf_counter


class Timer:
    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, *_):
        self.end = perf_counter()
        self.elapsed_ms = int((self.end - self.start) * 1000)
