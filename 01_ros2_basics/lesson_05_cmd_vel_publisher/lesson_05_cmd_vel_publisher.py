"""거북이를 직진시키는 Publisher 실습입니다."""

from geometry_msgs.msg import Twist  # noqa: F401
import rclpy
from rclpy.node import Node


class CmdVelPublisher(Node):
    """거북이 속도를 발행하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_05_cmd_vel_publisher')

        # 실습 1: /turtle1/cmd_vel에 Twist를 발행하는 Publisher를 만드세요.
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 실습 2: publish_velocity를 0.1초마다 실행하는 Timer를 만드세요.
        self.timer = self.create_timer(0.1, self.publish_velocity)

        self.linear_speed = 0.2

    def publish_velocity(self):
        """거북이의 속도를 발행합니다."""
        # 실습 3: Twist 메시지를 만들고 linear.x를 1.0으로 설정하여 발행하세요.
        msg = Twist()
        self.linear_speed += 0.01
        msg.linear.x = self.linear_speed
        msg.angular.z = 2.0
        self.publisher.publish(msg)


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = CmdVelPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
