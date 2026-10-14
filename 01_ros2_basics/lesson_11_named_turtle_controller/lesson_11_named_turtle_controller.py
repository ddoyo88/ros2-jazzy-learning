"""namespace로 거북이를 선택하는 실습입니다."""

from geometry_msgs.msg import Twist  # noqa: F401
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401


class NamedTurtleController(Node):
    """상대 토픽 이름으로 거북이를 제어하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_11_named_turtle_controller')

        # 실습 1: 상대 이름 cmd_vel에 Twist를 발행하세요.
        # self.publisher =

        # 실습 2: 상대 이름 pose를 구독하세요.
        # self.subscription =

        # 실습 3: publish_velocity를 0.1초마다 실행하세요.
        # self.timer =

    def publish_velocity(self):
        """현재 namespace의 거북이를 움직입니다."""
        # 실습 4: 직진 속도를 발행하세요.
        pass

    def on_pose(self, message):
        """현재 namespace의 거북이 위치를 처리합니다."""
        # 실습 5: x와 y를 출력하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = NamedTurtleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
