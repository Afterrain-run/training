#include <iostream>

int classify_offset(int offset) {
    if (offset < -10) {
        return -1;
    }
    if (offset > 10) {
        return 1;
    }
    return 0;
}

int main() {
    int offset = 0;
    std::cout << "输入目标相对中心的水平偏差（整数，左负右正）：";
    if (!(std::cin >> offset)) {
        std::cerr << "请输入整数\n";
        return 1;
    }

    int direction = classify_offset(offset);
    if (direction == -1) {
        std::cout << "目标偏左\n";
    } else if (direction == 1) {
        std::cout << "目标偏右\n";
    } else {
        std::cout << "目标居中\n";
    }
    return 0;
}
