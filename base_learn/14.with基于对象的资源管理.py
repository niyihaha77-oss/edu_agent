class FileOperate:
    def __enter__(self):
        print("准备前工作")
        return self


    def read_text(self,file_path):
        print(f"读取文件内容{file_path}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("清理释放资源")

if __name__ == '__main__':
    with FileOperate() as f:
        f.read_text('test.txt')