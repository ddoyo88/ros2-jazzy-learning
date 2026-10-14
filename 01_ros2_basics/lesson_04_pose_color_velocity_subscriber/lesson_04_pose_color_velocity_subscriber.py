"""위치, 색상, 속도를 한 노드에서 구독하는 실습입니다."""

from geometry_msgs.msg import Twist  # noqa: F401
import rclpy
from rclpy.node import Node
from turtlesim.msg import Color, Pose  # noqa: F401


class PoseColorVelocitySubscriber(Node):
    """세 가지 토픽의 값을 함께 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_04_pose_color_velocity_subscriber')
        self.pose = None
        self.color = None
        self.velocity = None

        # 실습 1: /turtle1/pose를 구독하세요.
        # self.pose_subscription =

        # 실습 2: /turtlesim/color_sensor를 구독하세요.
        # self.color_subscription =

        # 실습 3: /turtle1/cmd_vel을 구독하세요.
        # self.velocity_subscription =

        # 실습 4: print_values를 1초마다 실행하는 Timer를 만드세요.
        # self.timer =

    def on_pose(self, message):
        """최근 위치를 저장합니다."""
        # 실습 5: 받은 메시지를 self.pose에 저장하세요.
        pass

    def on_color(self, message):
        """최근 색상을 저장합니다."""
        # 실습 6: 받은 메시지를 self.color에 저장하세요.
        pass

    def on_velocity(self, message):
        """최근 속도를 저장합니다."""
        # 실습 7: 받은 메시지를 self.velocity에 저장하세요.
        pass

    def print_values(self):
        """세 토픽의 최근 값을 출력합니다."""
        # 실습 8: 세 메시지를 모두 받았을 때 값을 한 번에 출력하세요.
        pass


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = PoseColorVelocitySubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
