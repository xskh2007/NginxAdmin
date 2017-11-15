NginxAdmin
============

A web GUI for nginx configuration files management

About
========
NginxAdmin 是一个方便查看和管理nginx配置文件的web界面工具，使用Python开发。基于开源的轻量级python Web框架"Mole"
构建而成，配置文件解析用的美国休斯顿的一位大神写的模块。

Quick start
========
1. 下载源码
2. 配置config.py,加入要管理的nginx的配置文件路径等
3. 运行: python routes.py

注意点：
========
1、大括号前后需要有空格
2、同一个配置文件,同一个server_name，只能能写一个server(在nginx里面其实只要端口不一样是可以写多个server的，但是做起来比较麻烦暂时不支持)



Screenshots
========

![Screenshot](https://raw.githubusercontent.com/xskh2007/xskh2007.github.io/master/images/nginxadmin/nginxadmin1.jpg) 

