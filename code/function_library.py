import numpy as np


def controller_angle(target_val, prev_val):
    error_val = target_val - prev_val
    adj_target = prev_val + int(np.sign(error_val) * (abs(error_val) ** 0.2))
    return adj_target


def pid_controller(target_val, prev_val, prev_error):
    kp = 0.05
    ki = 0.1
    kd = 0.1

    error_val = target_val - prev_val
    integral = prev_error + error_val
    derivative = error_val - prev_error



    movement = int(kp * error_val + ki * integral + kd * derivative)
    movement = min(max(-2, movement), 2)
    adj_target = prev_val + movement
    return adj_target, error_val
