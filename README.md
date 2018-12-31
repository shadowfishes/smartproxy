# Autoproxy

HTTP代理服务器程序

想法：1、广泛爬取网上的免费代理并测试验证有效性，维护一个可供使用的代理池；  
      2、开启一个http代理服务器（使用网上获取的国外代理）访问google等服务；  
      3、解决网上免费代理经常失效，需要反复搜索和验证新代理等繁琐步骤。  
      4、项目仅支持py3.5以上版本，相关第三方依赖库请查阅requirements.txt。  

## 两个模块proxyserver和Pool，可独立分别使用
1、proxyserver代理服务器：支持上级代理功能设定，含日志功能，异步网络IO，完全使用标准库无依赖；
2、pool代理池：采用mongodb存储，维护一个可供使用的代理池（分国内和国外），支持定时任务，并发验证代理有效性。

## 使用示例：
查看帮助
python main.py --help
optional arguments:
  -h, --help     show this help message and exit
  --host HOST    设置代理服务器地址， 默认为127.0.0.1
  --port PORT    设置代理服务器端口，默认为8899
  --level LEVEL  设置日志级别，默认为INFO
  --auto AUTO    设置是否使用上级代理功能，默认关闭
使用：
python main.py --host 0.0.0.0 --auto True
当参数auto指定为True时，需要本机安装mongo等环境，第三方依赖库请查阅requirements；
当参数使用默认值时，无需安装第三方库。

