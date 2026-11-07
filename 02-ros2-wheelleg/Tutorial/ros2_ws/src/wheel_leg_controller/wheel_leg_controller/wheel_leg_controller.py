import csv
import math
import os

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState, Joy
from geometry_msgs.msg import Twist
from rm_msgs.msg import WheelLegCmd

from .vmc_cal import five_links_param
from .lqr_update import lqr_controller

def clamp(x,lo,hi):
    return max(lo,min(hi,x))

class PIDController:
    def __init__(self,kp,ki,kd,max_out,max_i,feedforward=0.0):
        self.kp,self.ki,self.kd=kp,ki,kd
        self.max_out,self.max_i=max_out,max_i
        self.feedforward=feedforward
        self.integral=0.0
        self.prev_error=0.0
    def compute(self,current,target):
        error=target-current
        self.integral=float(np.clip(self.integral+error,-self.max_i,self.max_i))
        derivative=error-self.prev_error
        self.prev_error=error
        out=self.kp*error+self.ki*self.integral+self.kd*derivative+self.feedforward
        return float(np.clip(out,-self.max_out,self.max_out))

class WheelLegController(Node):
    def __init__(self):
        super().__init__('wheel_leg_controller')
        self.dt=0.002
        self.wheel_radius=0.06
        self.target_length=0.10
        self.v_set=0.0           # 经爬坡限幅后的实际目标速度
        self.v_target=0.0        # /cmd_vel 给的原始目标速度
        self.target_w=0.0
        self.v_ramp=0.8          # 速度爬坡限幅 (m/s^2)，防指令阶跃顶翻倒立摆
        self.w_eff=0.0           # 仲裁后的偏航目标角速度

        # 手柄（加分项）：/joy 优先于 /cmd_vel，超时未收到自动退回
        self.joy_v=0.0
        self.joy_w=0.0
        self.joy_stamp=None
        self.deadzone=0.1
        self._prev_buttons=[0]*12
        self.declare_parameter('axis_v',1)       # 左摇杆上下（本机实测：推前=+1）
        self.declare_parameter('axis_w',3)       # 右摇杆左右
        self.declare_parameter('joy_timeout',0.5)

        self.fl_left=five_links_param(dt=self.dt)
        self.fl_right=five_links_param(dt=self.dt)
        self.lqr_left=lqr_controller(dt=self.dt)
        self.lqr_right=lqr_controller(dt=self.dt)
        self.L0_pid_left=PIDController(700.0,0.0,5.0,150.0,0.0)
        self.L0_pid_right=PIDController(700.0,0.0,5.0,150.0,0.0)
        self.yaw_pid_left=PIDController(0.5,0.0,1.0,2.0,0.0)
        self.yaw_pid_right=PIDController(0.5,0.0,1.0,2.0,0.0)

        self.imu=None
        self.last_stamp=None

        self.declare_parameter('record_path',
                               os.path.expanduser('~/venom_evidence/balance.csv'))
        rec=self.get_parameter('record_path').value
        os.makedirs(os.path.dirname(rec),exist_ok=True)
        self._csv=open(rec,'w',newline='')
        self._writer=csv.writer(self._csv)
        self._writer.writerow(['t_s','pitch_deg'])
        self._t0=None
        self.get_logger().info(f'记录 pitch 到 {rec}')

        self.cmd_pub=self.create_publisher(WheelLegCmd,'actuator_cmd',10)
        self.create_subscription(Imu,'imu',self.on_imu,10)
        self.create_subscription(JointState,'joint_states',self.on_joint_states,10)
        self.create_subscription(Twist,'cmd_vel',self.on_cmd_vel,10)
        self.create_subscription(Joy,'joy',self.on_joy,10)
        self.get_logger().info('wheel_leg_controller 已启动，等待 /joint_states …')

    def on_cmd_vel(self,msg):
        self.v_target=msg.linear.x
        self.target_w=msg.angular.z

    def on_joy(self,msg):
        ax=msg.axes
        av=int(self.get_parameter('axis_v').value)
        aw=int(self.get_parameter('axis_w').value)
        ax_v=ax[av] if len(ax)>av else 0.0
        ax_w=ax[aw] if len(ax)>aw else 0.0
        dz=self.deadzone
        # 左摇杆推前=+1 → 前进（实测符号）；右摇杆推右 → 右转（-z）
        self.joy_v=ax_v*0.6 if abs(ax_v)>dz else 0.0
        self.joy_w=-ax_w*2.0 if abs(ax_w)>dz else 0.0
        # LB/RB 边沿触发调目标腿长 ±0.005，限位 0.10~0.14
        b=list(msg.buttons)
        if len(b)>5:
            if b[5] and not self._prev_buttons[5]:
                self.target_length=min(0.14,self.target_length+0.005)
            if b[4] and not self._prev_buttons[4]:
                self.target_length=max(0.10,self.target_length-0.005)
            self._prev_buttons=(b+[0]*12)[:12]
        self.joy_stamp=self.get_clock().now()

    def on_imu(self,msg):
        self.imu=msg

    def on_joint_states(self,msg):
        if self.imu is None:
            return
        stamp=(msg.header.stamp.sec,msg.header.stamp.nanosec)
        if stamp==self.last_stamp:
            return
        self.last_stamp=stamp

        q=self.imu.orientation
        if q.x==0.0 and q.y==0.0 and q.z==0.0 and q.w==0.0:
            return
        s=2.0*(q.w*q.y-q.z*q.x)
        pitch=-math.asin(clamp(s,-1.0,1.0))
        gyro_pitch=-self.imu.angular_velocity.y
        gyro_yaw=self.imu.angular_velocity.z

        pos=dict(zip(msg.name,msg.position))
        vel=dict(zip(msg.name,msg.velocity))
        try:
            l1,l2=pos['left1'],pos['left2']
            r1,r2=pos['right1'],pos['right2']
            lw_p,rw_p=pos['leftwheel'],pos['rightwheel']
            lw_v,rw_v=vel['leftwheel'],vel['rightwheel']
        except KeyError as exc:
            self.get_logger().warn(f'缺少关节: {exc}')
            return

        common_pos=(lw_p-rw_p)/2.0
        common_speed=(lw_v-rw_v)/2.0

        # 移动平衡（加分项）：速度爬坡限幅 + x_b_set 站桩冻结/运动跟随
        # 手柄优先：joy_timeout 内收到 /joy 用手柄，否则用 /cmd_vel
        to=self.get_parameter('joy_timeout').value
        if self.joy_stamp is not None and \
           (self.get_clock().now()-self.joy_stamp).nanoseconds*1e-9<to:
            v_raw=self.joy_v
            w_raw=self.joy_w
        else:
            v_raw=self.v_target
            w_raw=self.target_w
        self.w_eff=w_raw
        dv_max=self.v_ramp*self.dt
        self.v_set+=clamp(v_raw-self.v_set,-dv_max,dv_max)
        # 只在运动时让 x_b_set 跟随当前位移；站桩时冻结，
        # 否则 x_b - x_b_set ≡ 0，位置环失效，车会匀速滑走不收敛
        if not (common_speed==0.0 and self.v_set==0.0):
            x_set=common_pos*self.wheel_radius
            self.lqr_left.x_b_set=x_set
            self.lqr_right.x_b_set=x_set

        l_phi1,l_phi4,l_wheel=self._control_leg(
            True,self.fl_left,self.lqr_left,self.L0_pid_left,self.yaw_pid_left,
            l1,l2,pitch,gyro_pitch,gyro_yaw,common_pos,common_speed)
        r_phi1,r_phi4,r_wheel=self._control_leg(
            False,self.fl_right,self.lqr_right,self.L0_pid_right,self.yaw_pid_right,
            r1,r2,pitch,gyro_pitch,gyro_yaw,common_pos,common_speed)

        t=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        if self._t0 is None:
            self._t0=t
        self._writer.writerow([f'{t-self._t0:.4f}',f'{math.degrees(pitch):.4f}'])

        cmd=WheelLegCmd()
        cmd.right_phi1,cmd.right_phi4=r_phi1,r_phi4
        cmd.left_phi1,cmd.left_phi4=l_phi1,l_phi4
        cmd.right_wheel,cmd.left_wheel=r_wheel,l_wheel
        vals=[cmd.right_phi1,cmd.right_phi4,cmd.left_phi1,
                cmd.left_phi4,cmd.right_wheel,cmd.left_wheel]
        if not all(math.isfinite(v) for v in vals):
            self.get_logger().warn('控制量含非有限数，跳过本帧')
            return
        self.cmd_pub.publish(cmd)

    def _control_leg(self,is_left,fl,lqr,L0_pid,yaw_pid,
                     m1,m2,pitch,gyro_pitch,gyro_yaw,common_pos,common_speed):
        leg_flag=1 if is_left else 0
        fl.forward_kinematics_cal(leg_flag,m1,m2,pitch,gyro_pitch)
        if is_left:
            lqr.states_update(1,fl,pitch,gyro_pitch,common_pos,common_speed,
                              self.wheel_radius)
        else:
            lqr.states_update(0,fl,pitch,gyro_pitch,-common_pos,-common_speed,
                              self.wheel_radius)
        lqr.calc_k_matrix_from_poly(fl.L_0)

        F0_ctrl=L0_pid.compute(fl.L_0,self.target_length)
        cos_t=math.cos(fl.theta)
        F0=(4.0/cos_t if cos_t!=0.0 else 0.0)+F0_ctrl
        F0=clamp(F0,-100.0,100.0)

        K=lqr.K
        T_p=(K[1]*lqr.theta+K[3]*lqr.d_theta
               +K[5]*(lqr.x_b-lqr.x_b_set)+K[7]*(lqr.v_b_whole-self.v_set)
               +K[9]*lqr.phi+K[11]*lqr.d_phi)
        wheel_T=(K[0]*lqr.theta+K[2]*lqr.d_theta
                   +K[4]*(lqr.x_b-lqr.x_b_set)+K[6]*(lqr.v_b_whole-self.v_set)
                   +K[8]*lqr.phi+K[10]*lqr.d_phi)

        yaw_ctrl=yaw_pid.compute(gyro_yaw,self.w_eff)
        wheel_cmd=(-wheel_T-yaw_ctrl) if is_left else (wheel_T-yaw_ctrl)
        wheel_cmd=clamp(wheel_cmd,-1.5,1.5)

        t0,t1=fl.VMC_torque_cal(F0,T_p)
        if is_left:
            return -t0,-t1,wheel_cmd
        return t0,t1,wheel_cmd

    def destroy_node(self):
        try:
            self._csv.close()
        except Exception:
            pass
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node=WheelLegController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__=='__main__':
    main()
