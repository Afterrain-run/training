# Venom 算法组培训

这里存放 Venom 算法组培训的示例程序和作业起始文件。每次作业使用一个独立文件夹：先读该文件夹的 README，再修改其中指定的文件。以后新增作业时，会继续在这里增加目录；保留同一个 Fork 即可接着学习。

## 从哪里开始

先准备好 Ubuntu 22.04、C++ 编译器、VS Code 和 Git，并登录自己的 GitHub 账号。第一次作业从编译一个小程序开始，再用编译警告和断点修复密码检查器；作业要求、测试数据和提交方法都写在作业目录中。

| 作业 | 内容 | 入口 |
| --- | --- | --- |
| 第一次作业 | Linux 基础、第一次 C++ 编译与调试、Git 提交 | [01-first-assignment](./01-first-assignment/README.md) |

第一次作业目录中的文件：

| 文件 | 用途 |
| --- | --- |
| [README.md](./01-first-assignment/README.md) | 题目要求、操作步骤、测试数据和提交方式。 |
| [direction.cpp](./01-first-assignment/direction.cpp) | 练习编译和调试的示例程序。 |
| [password_checker.cpp](./01-first-assignment/password_checker.cpp) | 需要修复的作业起始程序，里面故意保留了错误。 |
| `.gitignore` | 让 Git 忽略编译产生的程序等临时文件。 |

## 第一次作业怎么做

1. 点击页面右上角 **Fork**，把本仓库复制到自己的 GitHub 账号，仓库名保持 `training`；然后从自己的 Fork 页面复制 **Code → HTTPS** 地址。
2. 在 Ubuntu 终端克隆自己的 Fork。把下方 `USERNAME` 换成自己的 GitHub 用户名；`git remote -v` 显示的 `origin` 应是你自己的地址。

   ```bash
   mkdir -p ~/venom_cpp_basics
   cd ~/venom_cpp_basics
   git clone https://github.com/USERNAME/training.git
   cd training
   git remote -v
   cd 01-first-assignment
   code .
   ```

3. 按[第一次作业说明](./01-first-assignment/README.md)编译示例、调试并修复 `password_checker.cpp`。每次改完都要保存、重新编译和测试；保留题目要求的输入输出格式。
4. 只提交作业要求修改的源文件，把提交推送到自己的 Fork，再打开 Fork 页面确认修改已经出现。提交作业时提供自己的仓库链接，例如 `https://github.com/USERNAME/training`。第一次作业说明中有具体命令。

## 后续作业如何更新

不用为每次作业重新 Fork，也不用重复克隆到同一位置。新作业发布后，先在已有的本地仓库中用 `git status` 检查：如果还有未提交的修改，先完成提交。然后在仓库根目录运行以下命令；`git remote add upstream` 只需执行一次，如果 `git remote -v` 已显示 `upstream`，跳过这一行。

```bash
cd ~/venom_cpp_basics/training
git remote add upstream https://github.com/Venom-Algorithm/training.git
git fetch upstream
git merge --no-edit upstream/main
git push origin main
```

`upstream` 指算法组发布作业的仓库，`origin` 指你自己的 Fork；同步成功后，新作业目录会出现在本地，并上传到你的 Fork。如果 Git 报合并冲突，先用 `git status` 找出冲突文件，处理后再完成合并和推送，不要使用强制推送覆盖历史。
