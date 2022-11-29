class GlobalVariable:
    _global_dict = {}

    def _init(self):  # 初始化
        global _global_dict
        self._global_dict = {}

    def set_value(self, key, value):
        # 定义一个全局变量
        self._global_dict[key] = value

    def get_value(self, key):
        # 获得一个全局变量，不存在则提示读取对应变量失败
        try:
            return self._global_dict[key]
        except:
            print('读取' + key + '失败\r\n')

    def rm_value(self, key):
        try:
            return self._global_dict.pop(key)
        except:
            print('删除' + key + '失败\r\n')


glob_dict = GlobalVariable()
