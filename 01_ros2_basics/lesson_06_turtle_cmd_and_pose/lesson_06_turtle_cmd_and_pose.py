"""위치를 확인하며 벽을 피하는 실습입니다."""
import math

from geometry_msgs.msg import Twist  # noqa: F401
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401


class TurtleCmdAndPose(Node):
    """속도를 발행하고 위치를 구독하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_06_turtle_cmd_and_pose')
        self.pose = None

        # 실습 1: /turtle1/cmd_vel에 Twist를 발행하세요.
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 실습 2: /turtle1/pose를 구독하세요.
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)

        # 실습 3: publish_velocity를 0.1초마다 실행하세요.
        self.timer = self.create_timer(0.1, self.publish_velocity)

    def on_pose(self, message):
        """최근 위치를 저장합니다."""
        # 실습 4: 받은 메시지를 self.pose에 저장하세요.
        self.pose = message

    def publish_velocity(self): 
        """벽을 피하는 속도를 발행합니다."""

        if self.pose is None:
            return

        p = self.pose

        dx = math.cos(p.theta)
        dy = math.sin(p.theta)

        toward_wall = (
            (p.x < 1.5 and dx < 0)
            or (p.x > 9.5 and dx > 0)
            or (p.y < 1.5 and dy < 0)
            or (p.y > 9.5 and dy > 0)
        )

        msg = Twist()

        if toward_wall:
            msg.angular.z = 1.5
        else:
            msg.linear.x = 1.0

        self.publisher.publish(msg)

def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = TurtleCmdAndPose()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
