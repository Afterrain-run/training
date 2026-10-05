# Venom 算法组培训

这里存放 Venom 算法组培训用的示例程序和作业起始代码。每次作业单独放在一个文件夹中：先读文件夹里的 README，再按要求修改代码。以后发布新作业时，我们会在本仓库增加文件夹；你可以一直使用同一个 Fork。

## 从哪里开始

先准备好 Ubuntu 22.04、C++ 编译器、VS Code 和 Git，并登录自己的 GitHub 账号。第一次作业会用到编译警告和断点调试：你要找出密码检查程序中的错误并修好它。具体要求、测试数据和提交方法见作业目录。

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

1. 点击页面右上角 **Fork**，把本仓库复制到自己的 GitHub 账号，仓库名保持 `training`。然后在自己的 Fork 页面点击 **Code → HTTPS**，复制仓库地址。
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

3. 按[第一次作业说明](./01-first-assignment/README.md)调试并修复 `password_checker.cpp`。每次改完都要保存、重新编译和测试；不要改变题目要求的输入输出格式。
4. 只提交作业要求修改的源文件，把提交推送到自己的 Fork，再打开 Fork 页面确认修改已经出现。提交作业时提供自己的仓库链接，例如 `https://github.com/USERNAME/training`。第一次作业说明中有具体命令。

## 以后怎样获取新作业

假设算法组在这里增加了“第二次作业”文件夹，你之前 Fork 的仓库和电脑上的文件不会自动更新。不用重新 Fork 或克隆，只要把新内容同步到已有的仓库。

先让电脑记住算法组仓库的地址。下面的 `origin` 是你自己的 Fork，克隆时已自动设置；`upstream` 是算法组的仓库，需要添加一次。先运行 `git remote -v` 检查：如果已经显示 `upstream`，就跳过最后一条命令。

```bash
cd ~/venom_cpp_basics/training
git remote -v
git remote add upstream https://github.com/Venom-Algorithm/training.git
```

以后每次发布新作业时，在仓库根目录运行下面的命令。先看 `git status`：如果还有未提交的修改，先把它们提交，再继续。

```bash
cd ~/venom_cpp_basics/training
git status
git fetch upstream
git merge --no-edit upstream/main
git push origin main
```

`git fetch upstream` 下载算法组的新内容；`git merge --no-edit upstream/main` 把它加入电脑上的仓库，此时才能在本地看到新作业；`git push origin main` 再把更新上传到自己的 Fork。如果 Git 报错，把运行的命令、完整报错和 `git status` 的输出发给 AI，并说明你想做什么。合并遇到冲突时，先不要推送，更不要强制推送。
