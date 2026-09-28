# Venom 算法组：Linux 与 C++ 入门练习

本仓库配套《Venom 算法组：Linux 基础与第一次 C++ 开发》。使用 Ubuntu 22.04、C++17、VS Code 和 Git 完成练习。

`direction.cpp` 是课堂上的方向判断示例；`password_checker.cpp` 是需要排错的起始程序，里面故意保留了编译警告和逻辑错误。

## 作业要求

修复 `password_checker.cpp`，使密码同时满足以下条件时输出 `VALID`，否则输出 `INVALID`：长度至少 10 个字符；至少包含一个大写字母、一个小写字母和一个数字；不包含使用者的名或姓（区分大小写）。程序从标准输入读取一行“名 姓 密码”，三项之间用空格隔开。保持文件名和输入输出格式不变。本练习参考了 [UC Berkeley CS61C 的调试 Lab](https://cs61c.org/fa26/labs/lab02/)，使用 C++17 和 VS Code 完成。

## Fork、修改、提交

1. 打开本仓库页面，点击右上角 **Fork**，在自己的 GitHub 账号下创建副本，仓库名保持 `training`。
2. 在自己的 Fork 页面点击 **Code → HTTPS**，复制仓库地址。在 Ubuntu 终端中进入练习目录并克隆。下面命令中的 `USERNAME` 要换成自己的 GitHub 用户名：

   ```bash
   cd ~/venom_cpp_basics
   git clone https://github.com/USERNAME/training.git
   cd training
   git remote -v
   code .
   ```

   `git remote -v` 应显示你自己 Fork 的地址。此后都在这个 `training` 文件夹中修改和运行程序。
3. 按教程修复 `password_checker.cpp`。文件开头用注释写上姓名，简要说明数字判断、长度判断和范围边界原先各有什么问题，再写一组自己设计的测试输入及预期输出。
4. 编译和运行。每次修改后都要重新编译；最终编译不应出现警告。

   ```bash
   g++ -std=c++17 -Wall -Wextra -g password_checker.cpp -o password_checker
   ./password_checker
   ```

5. 用下表逐一测试，每行重新运行一次程序：

   | 输入 | 正确输出 |
   | --- | --- |
   | `Li Wang Bb23456781` | `VALID` |
   | `Li Wang Bb234567812` | `VALID` |
   | `Li Wang Aaabcdefg9` | `VALID` |
   | `Li Wang Zzabcdefg0` | `VALID` |
   | `Li Wang Bb2345678` | `INVALID` |
   | `Li Wang bb23456781` | `INVALID` |
   | `Li Wang BB23456781` | `INVALID` |
   | `Li Wang Bbabcdefgh` | `INVALID` |
   | `Li Wang BbLi234567` | `INVALID` |
   | `Li Wang BbWang2345` | `INVALID` |

6. 第一次从这台 Ubuntu 电脑推送到 GitHub 时，安装 GitHub CLI 并登录。终端会给出一次性验证码；按提示在浏览器中输入并授权。

   ```bash
   sudo apt install -y gh
   gh auth login -h github.com -p https --web
   gh auth setup-git
   gh auth status
   ```

7. 确认修改内容，然后提交并推送到自己的 Fork：

   ```bash
   git status
   git diff -- password_checker.cpp
   git add password_checker.cpp
   git commit -m "Fix password checker"
   git push origin main
   ```

打开自己的 Fork 页面，确认能看到刚才的提交。提交作业时提供自己 Fork 的仓库链接，例如 `https://github.com/USERNAME/training`。
