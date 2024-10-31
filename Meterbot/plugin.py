import os
import sys
import importlib,importlib.util
import json
from .bot import _Bot


pluginspath = f'{sys.path[0]}/plugins'

class Plugin():
    def __init__(self,Bot,pluginspath=pluginspath) -> None:
        _Bot._bot = Bot
        self.Bot = Bot
        self.dir_list = []
        self.py_list = []
        self.pluginspath = pluginspath
        dir = os.listdir(pluginspath)
        for f in dir:
            if os.path.isdir(os.path.join(pluginspath,f)) and f != '__pycache__':
                self.dir_list.append(f)
            elif f.endswith('.py') and f != '__init__.py':
                self.py_list.append(f)

        #加载插件
    def load_plugins(self):
        for f in self.py_list:
            try:
                module_path = f"{self.pluginspath}/{f}"
                spec = importlib.util.spec_from_file_location(f, module_path)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
                # load_model.main(self.Bot)
                self.Bot.logger.info(f"{f} load successed")
                print(f"插件{f}加载成功")
            except:
                self.Bot.logger.error(f"{f} load failed")
                print(f"插件{f}加载失败")
        for f in self.dir_list:
            try:
                module_path = f"{self.pluginspath}/{f}/main.py"
                spec = importlib.util.spec_from_file_location(f, module_path)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
                self.Bot.logger.info(f"{f} load successed")
                print(f"插件{f}加载成功")
            except:
                self.Bot.logger.error(f"{f} load failed")
                print(f"插件{f}加载失败")
    
    def load_plugin(self,name): 
        if name.endswith('.py') and name != '__init__.py': 
            try:
                module_path = f"{self.pluginspath}/{name}"
                spec = importlib.util.spec_from_file_location(name, module_path)
                # my_module = importlib.util.module_from_spec(spec)
                # sys.modules[spec.name] = my_module
                # spec.loader.exec_module(my_module)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
                self.Bot.logger.info(f"{name} load successed")
                print(f"插件{name}加载成功")
            except:
                self.Bot.logger.error(f"{name} load failed")
                print(f"插件{name}加载失败")
        else:
            try:
                module_path = f"{self.pluginspath}/{name}/main.py"
                spec = importlib.util.spec_from_file_location(name, module_path)
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
                self.Bot.logger.info(f"{name} load successed")
                print(f"插件{name}加载成功")
            except:
                self.Bot.logger.error(f"{name} load failed")
                print(f"插件{name}加载失败")
