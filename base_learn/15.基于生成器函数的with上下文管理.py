from contextlib import contextmanager


# with
# 1.准备工作
# 2.返回资源
# 3.释放资源
@contextmanager
def file_read():
    print('准备前工作')  # 类比__enter__
    yield 'test'  # 类比return 值，但不是return

    print('释放资源')  # 类比__exit__
    pass


if __name__ == '__main__':
    with file_read() as f:
        print(f)
        pass
