#!/usr/bin/python3
#coding:utf-8
import os
import sys
import time
import logging
from tool.logtool.singleton import Singleton
 
'''
调用方法
critical("这是一个 critical 级别的问题！")
error("这是一个 error 级别的问题！")
warning("这是一个 warning 级别的问题！")
info("这是一个 info 级别的问题！")
debug("这是一个 debug 级别的问题！")
 
log(50, "这是一个 critical 级别的问题的另一种写法！")
log(40, "这是一个 error 级别的问题的另一种写法！")
log(30, "这是一个 warning 级别的问题的另一种写法！")
log(20, "这是一个 info 级别的问题的另一种写法！")
log(10, "这是一个 debug 级别的问题的另一种写法！")
 
log(51, "这是一个 Level 51 级别的问题！")
log(11, "这是一个 Level 11 级别的问题！")
log(9, "这条日志等级低于 debug，不会被打印")
log(0, "这条日志同样不会被打印")
'''
 
@Singleton
class Logger:
    def __init__(self, set_level="INFO",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 log_name=time.strftime("%Y-%m-%d.log", time.localtime()),
                 log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../log"),
                 use_console=True):
        """
        :param set_level: 日志级别["NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"]，默认为INFO
        :param name: 日志中打印的name，默认为运行程序的name
        :param log_name: 日志文件的名字，默认为当前时间（年-月-日.log）
        :param log_path: 日志文件夹的路径，默认路径为根目录中的log文件夹
        :param use_console: 是否在控制台打印，默认为True
        """
        if not set_level:
            set_level = self._exec_type()       # 设置set_level为None，自动获取当前运行模式
        self.__logger = logging.getLogger(name)
        self.setLevel(getattr(logging, set_level.upper()) if hasattr(logging, set_level.upper()) else logging.INFO)     # 设置日志级别
        if not os.path.exists(log_path):        # 创建日志目录
            os.makedirs(log_path)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler_list = list()
        handler_list.append(logging.FileHandler(os.path.join(log_path, log_name),encoding='utf-8'))
        if use_console:
            handler_list.append(logging.StreamHandler())
        for handler in handler_list:
            handler.setFormatter(formatter)
            self.addHandler(handler)
 
    def __getattr__(self, item):
        return getattr(self.logger, item)
 
    @property
    def logger(self):
        return self.__logger
 
    @logger.setter
    def logger(self, func):
        self.__logger = func
 
    def _exec_type(self):
        return "DEBUG" if os.environ.get("IPYTHONENABLE") else "INFO"

'''
--------------------- 
作者：伪善者 
来源：CSDN 
原文：https://blog.csdn.net/qq_42486920/article/details/83020693 
版权声明：本文为博主原创文章，转载请附上博文链接！
'''