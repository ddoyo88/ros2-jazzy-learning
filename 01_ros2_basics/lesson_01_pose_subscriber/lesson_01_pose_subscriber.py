"""거북이의 위치를 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401


class PoseSubscriber(Node):
    """거북이 위치를 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_01_pose_subscriber')

        # 실습 1: /turtle1/pose를 구독하는 Subscription을 만드세요.
        # self.subscription =

    def on_pose(self, message):
        """수신한 위치를 처리합니다."""
        # 실습 2: message의 x, y, theta를 출력하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = PoseSubscriber()

    try:
        # 실습 3: node를 spin으로 실행하세요.
        pass
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
