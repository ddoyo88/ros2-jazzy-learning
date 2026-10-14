"""위치에 따라 펜 색상을 바꾸는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401
from turtlesim.srv import SetPen  # noqa: F401


class RegionPenClient(Node):
    """왼쪽과 오른쪽 영역의 펜 색상을 바꾸는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_10_region_pen_client')
        self.current_region = None

        # 실습 1: /turtle1/set_pen의 Client를 만드세요.
        self.client = self.create_client(SetPen, '/turtle1/set_pen')

        # 실습 2: /turtle1/pose를 구독하세요.
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)

    def on_pose(self, message):
        """현재 위치에 맞는 펜 색상을 요청합니다."""
        # 실습 3: message.x를 기준으로 left와 right를 구분하세요.
        if message.x < 5.0:
            new_region = 'left'
        else:
            new_region = 'right'

        # 실습 4: 이전과 같은 영역이면 서비스를 호출하지 마세요.
        if new_region == self.current_region:
            return

        self.current_region = new_region

        # 실습 5: 왼쪽은 노랑, 오른쪽은 초록으로 변경하세요.
        self.call_set_pen_service(new_region)

    def call_set_pen_service(self, region):
        """펜 색상을 변경하는 서비스를 호출합니다."""
        # 실습 6: 서비스 요청을 생성하고 호출하세요.    
        req = SetPen.Request()
        if region == 'left':
            req.r = 255
            req.g = 255
            req.b = 0
        elif region == 'right':
            req.r = 0
            req.g = 255
            req.b = 0
        self.client.call_async(req)


def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = RegionPenClient()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
