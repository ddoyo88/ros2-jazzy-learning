"""거북이 아래의 색상을 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Color  # noqa: F401


class ColorSubscriber(Node):
    """RGB 색상을 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_02_color_subscriber')

        # 실습 1: /turtlesim/color_sensor를 구독하세요.
        # self.subscription =

    def on_color(self, message):
        """수신한 색상을 처리합니다."""
        # 실습 2: message의 r, g, b를 출력하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = ColorSubscriber()

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
