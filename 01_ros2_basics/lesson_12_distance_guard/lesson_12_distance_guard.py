"""두 거북이의 거리를 이용한 충돌 방지 실습입니다."""

import math
import random  # noqa: F401

from geometry_msgs.msg import Twist  # noqa: F401
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401


SAFE_DISTANCE = 2.0


def distance_between(first_pose, second_pose):
    """두 거북이 사이의 거리를 계산합니다."""
    return math.hypot(
        first_pose.x - second_pose.x,
        first_pose.y - second_pose.y,
    )


class DistanceGuard(Node):
    """turtle2가 turtle1에 가까워지면 멈추는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_12_distance_guard')
        self.turtle1_pose = None
        self.turtle2_pose = None

        # 실습 1: /turtle1/pose를 구독하세요.
        # self.turtle1_subscription =

        # 실습 2: /turtle2/pose를 구독하세요.
        # self.turtle2_subscription =

        # 실습 3: /turtle2/cmd_vel에 Twist를 발행하세요.
        # self.publisher =

        # 실습 4: control_turtle2를 0.1초마다 실행하세요.
        # self.timer =

    def on_turtle1_pose(self, message):
        """turtle1의 최근 위치를 저장합니다."""
        # 실습 5: 받은 메시지를 self.turtle1_pose에 저장하세요.
        pass

    def on_turtle2_pose(self, message):
        """turtle2의 최근 위치를 저장합니다."""
        # 실습 6: 받은 메시지를 self.turtle2_pose에 저장하세요.
        pass

    def control_turtle2(self):
        """거리에 따라 turtle2의 속도를 발행합니다."""
        # 실습 7: 가까우면 멈추고, 멀면 임의 방향으로 움직이게 하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = DistanceGuard()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
