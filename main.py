#! /usr/bin/env python
# -*- coding:utf-8 -*-
# 主程序

import sys
import os
import logging
import argparse

import server


def mklogdir():
    """
    创建代理服务器的日志目录
    windows平台在同名目录下 ~/proxy_log， linux平台在/var/log/proxy.log

    """
    platform = sys.platform
    if platform.startswith("win"):
        logpath = os.path.abspath(os.path.dirname(__file__)) + os.path.sep + "proxy_log"
        logging.debug("日志目录路径：%s" % logpath)
        makedir(logpath)
    elif platform.startswith("linux"):
        logpath = r"/var/log/proxy.log"
        logging.debug("日志目录路径：%s" % logpath)
        makedir(logpath)


def makedir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        logging.debug("创建日志目录")
    elif os.path.isfile(path):
        logging.error(
            "存在重名文件，无法创建日志目录")
        raise OSError(
            "存在重名文件，无法创建日志目录")
    else:
        logging.debug("日志目录已存在")


def main():
    logger = logging.getLogger("main")
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="设置代理服务器地址， 默认为127.0.0.1")
    parser.add_argument("--port", default=8899, type=int, help="设置代理服务器端口，默认为8899")
    parser.add_argument("--level", default="INFO", help="设置日志级别，默认为INFO")
    parser.add_argument("--auto", default="False", help="设置是否使用上级代理功能，默认关闭")
    args = parser.parse_args()
    level_args = r"logging." + args.level.upper()
    logging.basicConfig(level=eval(level_args),
                        format="%(asctime)s - %(filename)s line: %(lineno)s - %(levelname)s - %(message)s",
                        datefmt='%Y-%m-%d %A %H:%M:%S',
                        )

    if sys.version.startswith("3"):
        try:
            myserver = server.Server(args.host, args.port, auto=args.auto)
            mklogdir()
            myserver.run()
        except KeyboardInterrupt:
            logger.info("服务器被终止")
        except OSError as err:
            logger.exception(err)

    else:
        logging.error("代理服务器仅支持py3")


if __name__ == "__main__":
    main()
