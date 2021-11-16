# 加人模式

## 脚本使用方式

1. 将两个文件clone到本地。
2. 在`user_config.py`里修改成自己的账户密码。
3. 运行`python lecture_select.py`，Enjoy!

注：可能需要装`requests`、`retry`包，遇到没有的装一下就行，都是常见的包，懒得搞requirement了


## 模块复用

其中有个单独的模块解析了统一登陆平台的登陆流程，爬取其他所有信息均可复用，已经单独抽取出来变成了功能模块[USTC_Auth](https://github.com/VincentJYZhang/USTC_Auth)，欢迎使用。

https://github.com/VincentJYZhang/USTC_Auth
