"""두 번째 거북이를 만드는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn  # noqa: F401


class SpawnClient(Node):
    """새 거북이 생성을 요청하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_09_spawn_client')

        # 실습 1: /spawn의 Client를 만드세요.
        self.client = self.create_client(Spawn, '/spawn')   

    def send_request(self):
        self.client.wait_for_service()
        """거북이 생성 요청을 보냅니다."""
        # 실습 2: 위치와 이름이 포함된 Spawn 요청 메시지를 만드세요.
        request = Spawn.Request()
        request.x = 2.0
        request.y = 2.0
        request.theta = 0.0
        request.name = 'turtle2'

        # 실습 3: call_async로 요청을 보내고 Future를 반환하세요.
        return self.client.call_async(request)


def main(args=None):
    """서비스를 호출합니다."""
    rclpy.init(args=args)
    node = SpawnClient()

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
