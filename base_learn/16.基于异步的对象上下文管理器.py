import asyncio


class FileOperate:
    async def __aenter__(self):
        print("准备前工作")
        return self


    def read_text(self,file_path):
        print(f"读取文件内容{file_path}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("清理释放资源")
async def main():
    async with FileOperate() as f:
        f.read_text('test.txt')
if __name__ == '__main__':
    asyncio.run(main())