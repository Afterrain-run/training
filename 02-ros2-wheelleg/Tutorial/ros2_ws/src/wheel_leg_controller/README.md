# wheel_leg_controller

ROS2 轮腿自平衡控制器（VMC + LQR），配合 `wheel_leg_sim` 仿真器使用。
控制器与仿真器为两个独立进程，通过话题通信；控制器不依赖 mujoco。

## 环境

- Ubuntu 24.04 + ROS 2 Jazzy + Python 3.12（conda 环境 rm_ros2）

## 话题接口

| 方向 | 话题 | 类型 | 说明 |
|---|---|---|---|
| 订阅 | /imu | sensor_msgs/Imu | 机身姿态与角速度 |
| 订阅 | /joint_states | sensor_msgs/JointState | 4 关节 + 2 轮位置/速度 || 发布 | /actuator_cmd | rm_msgs/WheelLegCmd | 4 关节力矩 + 2 轮力矩 |

事件驱动契约：仿真器每收到一条 /actuator_cmd 推进一步（dt=0.002s）并回发状态；
控制器按 /joint_states 的 header.stamp 去重，心跳帧不重复触发控制。

## 控制结构

- 五连杆 VMC：关节力矩 ↔ 虚拟腿长方向力 F0 / 摆杆力矩 Tp（vmc_cal.py）
- LQR：6 维状态 [theta, d_theta, x_b, v_b, phi, d_phi]，K 矩阵由 12×4
  多项式按虚拟腿长 L0 实时拟合（lqr_update.py）
- 腿长环：重力前馈 4/cos(theta) + PD（kp=700, kd=5）
- yaw 环：PD（kp=0.5, kd=1.0）
- 算法文件复用自 Wheel_Leg/LQR_VMC/，与入口文件同级、相对导入

## 运行

```bash
# 终端 A
ros2 run wheel_leg_sim wheel_leg_sim
# 终端 B
ros2 run wheel_leg_controller wheel_leg_controller
```
验收实测
连续平衡 142.78 s（要求 ≥ 5 s）
pitch 全程 −4.11° ~ 4.92°（要求 |pitch| < 10°），末 1 s 收敛至 −0.11°
采样 71391 点 / 142.78 s ≈ 500 Hz，与事件驱动 dt=0.002s 一致
pitch.png
录屏证据：
https://pan.baidu.com/s/1EyrCKBvsvp3BKuyP-DeVQg?pwd=atm4
