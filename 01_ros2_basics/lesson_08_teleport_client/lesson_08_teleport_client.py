"""거북이를 순간이동시키는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute  # noqa: F401


class TeleportClient(Node):
    """순간이동 서비스를 요청하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_08_teleport_client')

        # 실습 1: /turtle1/teleport_absolute의 Client를 만드세요.
        self.client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')

    def send_request(self):
        self.client.wait_for_service()
        """순간이동 요청을 보냅니다."""
        # 실습 2: x=2.0, y=2.0, theta=0.0인 요청 메시지를 만드세요.
        request = TeleportAbsolute.Request()    
        request.x = 2.0
        request.y = 2.0
        request.theta = 0.0 

        # 실습 3: call_async로 요청을 보내고 Future를 반환하세요.
        return self.client.call_async(request)


def main(args=None):
    """서비스를 호출합니다."""
    rclpy.init(args=args)
    node = TeleportClient()

    try:
        # 실습 4: 서비스가 준비될 때까지 기다리세요.
        future = node.send_request()
        # 실습 5: 요청을 보내고 완료될 때까지 spin하세요.
        rclpy.spin_until_future_complete(node, future)
        response = future.result()

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
