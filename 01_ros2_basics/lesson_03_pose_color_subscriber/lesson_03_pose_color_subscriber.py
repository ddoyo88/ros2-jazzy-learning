"""위치와 색상을 한 노드에서 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Color, Pose  # noqa: F401


class PoseColorSubscriber(Node):
    """위치와 색상을 함께 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_03_pose_color_subscriber')
        self.pose = None
        self.color = None

        # 실습 1: /turtle1/pose를 구독하세요.
        # self.pose_subscription =

        # 실습 2: /turtlesim/color_sensor를 구독하세요.
        # self.color_subscription =

        # 실습 3: print_values를 1초마다 실행하는 Timer를 만드세요.
        # self.timer =

    def on_pose(self, message):
        """최근 위치를 저장합니다."""
        # 실습 4: 받은 Pose 메시지를 self.pose에 저장하세요.
        pass

    def on_color(self, message):
        """최근 색상을 저장합니다."""
        # 실습 5: 받은 Color 메시지를 self.color에 저장하세요.
        pass

    def print_values(self):
        """최근 위치와 색상을 출력합니다."""
        # 실습 6: 두 메시지를 모두 받았을 때 위치와 색상을 출력하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = PoseColorSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
