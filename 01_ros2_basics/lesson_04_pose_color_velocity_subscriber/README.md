
# 1. 이번 실습에서 만들 프로그램

이번 프로그램은 다음 세 가지 정보를 받아.

| 구분 | 토픽 이름 | 메시지 타입 | 확인할 데이터 |
|---|---|---|---|
| 위치 | `/turtle1/pose` | `turtlesim/msg/Pose` | x, y, 방향 |
| 색상 | `/turtle1/color_sensor` | `turtlesim/msg/Color` | R, G, B |
| 속도 | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | 선속도, 각속도 |

참고로 네 코드의 주석에는 `/turtlesim/color_sensor`라고 적혀 있지만, 기본 turtlesim의 색상 토픽 이름은 `/turtle1/color_sensor`야.

전체적인 데이터 흐름을 살펴보자.

```text
                    turtlesim
                        │
          ┌─────────────┼──────────────┐
          │             │              │
          ▼             ▼              ▼
  /turtle1/pose  /turtle1/color_sensor  /turtle1/cmd_vel
          │             │              │
          ▼             ▼              ▼
      on_pose()     on_color()     on_velocity()
          │             │              │
          ▼             ▼              ▼
      self.pose     self.color     self.velocity
          │             │              │
          └─────────────┼──────────────┘
                        │
                        ▼
                  print_values()
                    1초마다
                        │
                        ▼
              세 가지 데이터 출력
```

이번 실습의 핵심은 **각 토픽의 데이터를 별도로 저장하고, 타이머를 이용해 세 가지 정보를 함께 출력하는 것**이야.

---

# 2. 완성된 코드

먼저 전체 코드를 확인해 보자.

```python
"""위치, 색상, 속도를 한 노드에서 구독하는 실습입니다."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Color, Pose


class PoseColorVelocitySubscriber(Node):
    """세 가지 토픽의 값을 함께 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_04_pose_color_velocity_subscriber')

        self.pose = None
        self.color = None
        self.velocity = None

        # 실습 1: 위치 토픽 구독
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10
        )

        # 실습 2: 색상 토픽 구독
        self.color_subscription = self.create_subscription(
            Color,
            '/turtle1/color_sensor',
            self.on_color,
            10
        )

        # 실습 3: 속도 토픽 구독
        self.velocity_subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.on_velocity,
            10
        )

        # 실습 4: 1초마다 데이터 출력
        self.timer = self.create_timer(
            1.0,
            self.print_values
        )

    def on_pose(self, message):
        """최근 위치를 저장합니다."""
        self.pose = message

    def on_color(self, message):
        """최근 색상을 저장합니다."""
        self.color = message

    def on_velocity(self, message):
        """최근 속도를 저장합니다."""
        self.velocity = message

    def print_values(self):
        """세 토픽의 최근 값을 출력합니다."""
        if (
            self.pose is not None
            and self.color is not None
            and self.velocity is not None
        ):
            self.get_logger().info(
                f'위치: x={self.pose.x:.2f}, '
                f'y={self.pose.y:.2f}, '
                f'theta={self.pose.theta:.2f} | '
                f'색상: R={self.color.r}, '
                f'G={self.color.g}, '
                f'B={self.color.b} | '
                f'속도: linear.x={self.velocity.linear.x:.2f}, '
                f'angular.z={self.velocity.angular.z:.2f}'
            )


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
```

이제 중요한 부분을 하나씩 살펴보자.

# 3. 실습 1: 위치 토픽 구독하기

```python
self.pose_subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

지난 실습에서 작성했던 코드와 동일해.

`create_subscription()`은 다음 네 가지 정보를 사용해 구독을 등록해.

```python
self.create_subscription(
    메시지_타입,
    토픽_이름,
    콜백_함수,
    큐_크기
)
```

각각의 의미는 다음과 같아.

| 코드 | 의미 |
|---|---|
| `Pose` | 수신할 메시지 타입 |
| `'/turtle1/pose'` | 구독할 토픽 이름 |
| `self.on_pose` | 메시지를 받으면 실행할 콜백 함수 |
| `10` | QoS의 이력 설정에서 사용하는 깊이 |

마지막의 `10`은 단순히 메시지를 정확히 10개만 받는다는 뜻이 아니야. 기본 QoS 설정에서 `KEEP_LAST` 방식으로 보관할 메시지의 깊이를 지정하는 값이야.

## 위치 메시지에는 무엇이 있을까?

`Pose` 메시지는 다음과 같은 데이터를 가지고 있어.

```text
x
y
theta
linear_velocity
angular_velocity
```

각 항목의 의미는 다음과 같아.

- `x`: 거북이의 가로 좌표
- `y`: 거북이의 세로 좌표
- `theta`: 거북이가 바라보는 방향
- `linear_velocity`: 현재 선속도
- `angular_velocity`: 현재 각속도

여기서 주의할 점이 있어.

`Pose` 안에도 속도 정보가 있지만, 이번 실습에서는 별도의 `/turtle1/cmd_vel` 토픽을 구독해서 **이동 명령으로 전달되는 속도**를 확인할 거야.

두 정보는 서로 관련이 있지만 동일한 개념은 아니야.

---

# 4. 실습 2: 색상 토픽 구독하기

```python
self.color_subscription = self.create_subscription(
    Color,
    '/turtle1/color_sensor',
    self.on_color,
    10
)
```

이 코드는 색상 센서 토픽을 구독해.

여기서 `Color`는 다음 세 가지 값을 가지고 있어.

```text
r
g
b
```

각각 빨간색, 초록색, 파란색의 강도를 의미해.

예를 들어 다음과 같은 메시지가 들어왔다고 가정해 보자.

```text
r: 255
g: 0
b: 0
```

이것은 빨간색에 해당하는 RGB 값이야.

색상 토픽을 실제로 확인하고 싶다면 turtlesim이 실행된 상태에서 다음 명령어를 입력해 봐.

```bash
ros2 topic echo /turtle1/color_sensor
```

실시간으로 색상 센서 메시지를 확인할 수 있어.

종료할 때는 `Ctrl + C`를 누르면 돼.

---

# 5. 실습 3: 속도 토픽 구독하기

이번 실습에서 새롭게 추가되는 가장 중요한 부분이야.

```python
self.velocity_subscription = self.create_subscription(
    Twist,
    '/turtle1/cmd_vel',
    self.on_velocity,
    10
)
```

위치와 색상 구독 코드와 구조가 같지?

다만 이번에는 메시지 타입이 `Twist`라는 점이 달라.

## 5-1. `Twist`는 무엇일까?

```python
from geometry_msgs.msg import Twist
```

`Twist`는 로봇의 선속도와 각속도를 표현하기 위한 메시지 타입이야.

내부 구조는 다음과 같아.

```text
Twist
 ├── linear
 │    ├── x
 │    ├── y
 │    └── z
 │
 └── angular
      ├── x
      ├── y
      └── z
```

`linear`는 직선 방향의 속도, `angular`는 회전 방향의 속도를 표현해.

각 항목은 3차원 벡터 형태로 구성되어 있어.

일반적인 2차원 이동 로봇에서는 다음 두 항목을 주로 사용해.

```python
message.linear.x
message.angular.z
```

- `linear.x`: 앞뒤 방향의 선속도
- `angular.z`: 수직축을 중심으로 회전하는 각속도

여기서 중요한 것은 **`Twist` 메시지 자체가 실제로 측정된 속도인지, 이동 명령인지에 따라 의미가 달라진다**는 점이야.

이번에는 `/turtle1/cmd_vel`을 구독하므로 거북이에게 전달되는 속도 명령을 확인하는 거야.

## 5-2. 속도 명령을 직접 확인하기

turtlesim이 실행된 상태에서 다음 명령어를 입력해 봐.

```bash
ros2 topic echo /turtle1/cmd_vel
```

그다음 다른 터미널에서 다음 명령어를 실행해.

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

이 명령은 다음과 같은 속도 명령을 한 번 발행해.

```text
linear.x = 1.0
angular.z = 0.5
```

여기서 `--once`는 메시지를 한 번만 발행한다는 뜻이야.

거북이가 명령을 받으면 앞으로 움직이면서 회전할 수 있어. `cmd_vel`은 명령을 전달하는 토픽이므로, 한 번 발행한 명령이 계속 유지되는지 여부는 수신 노드의 동작 방식에 따라 달라질 수 있어.

---

# 6. 실습 4: 타이머 만들기

```python
self.timer = self.create_timer(
    1.0,
    self.print_values
)
```

이 부분은 지난 실습과 같아.

`create_timer()`는 일정한 시간 간격으로 함수를 실행하도록 등록하는 기능이야.

```python
self.create_timer(시간_간격, 실행할_함수)
```

여기서는 다음과 같이 작성했어.

```python
1.0
```

1초 간격이라는 뜻이야.

```python
self.print_values
```

1초마다 실행할 함수야.

이 구조를 사용하면 세 토픽에서 메시지가 수십 번씩 들어오더라도 출력은 약 1초 간격으로 제한할 수 있어.

정리하면 다음과 같아.

```text
위치 메시지 수신 → 위치 저장
색상 메시지 수신 → 색상 저장
속도 메시지 수신 → 속도 저장

타이머 실행
    ↓
최신 위치 읽기
최신 색상 읽기
최신 속도 읽기
    ↓
한 번에 출력
```

---

# 7. 실습 5~7: 세 가지 메시지 저장하기

이번 실습에서는 각각의 콜백 함수가 데이터를 저장하도록 작성하면 돼.

### 위치 저장

```python
def on_pose(self, message):
    """최근 위치를 저장합니다."""
    self.pose = message
```

### 색상 저장

```python
def on_color(self, message):
    """최근 색상을 저장합니다."""
    self.color = message
```

### 속도 저장

```python
def on_velocity(self, message):
    """최근 속도를 저장합니다."""
    self.velocity = message
```

세 함수의 구조가 거의 동일하지?

차이는 어느 변수에 메시지를 저장하는지뿐이야.

| 콜백 함수 | 저장하는 변수 |
|---|---|
| `on_pose()` | `self.pose` |
| `on_color()` | `self.color` |
| `on_velocity()` | `self.velocity` |

예를 들어 속도 메시지가 다음과 같이 전달되었다고 가정해 보자.

```text
linear:
  x: 1.0
  y: 0.0
  z: 0.0

angular:
  x: 0.0
  y: 0.0
  z: 0.5
```

다음 코드가 실행되면,

```python
self.velocity = message
```

메시지 전체가 `self.velocity`에 저장돼.

이후 다른 함수에서 다음과 같이 값을 읽을 수 있어.

```python
self.velocity.linear.x
self.velocity.angular.z
```

**콜백 함수는 메시지를 받는 역할, `self.velocity`는 받은 메시지를 보관하는 역할**이라고 이해하면 돼.

---

# 8. 실습 8: 세 가지 값을 한 번에 출력하기

마지막 실습이야.

```python
def print_values(self):
    """세 토픽의 최근 값을 출력합니다."""
    if (
        self.pose is not None
        and self.color is not None
        and self.velocity is not None
    ):
        self.get_logger().info(
            f'위치: x={self.pose.x:.2f}, '
            f'y={self.pose.y:.2f}, '
            f'theta={self.pose.theta:.2f} | '
            f'색상: R={self.color.r}, '
            f'G={self.color.g}, '
            f'B={self.color.b} | '
            f'속도: linear.x={self.velocity.linear.x:.2f}, '
            f'angular.z={self.velocity.angular.z:.2f}'
        )
```

이 부분에는 중요한 개념이 세 가지 있어.

## 8-1. `if`문으로 메시지 수신 여부 확인하기

```python
if (
    self.pose is not None
    and self.color is not None
    and self.velocity is not None
):
```

세 가지 메시지를 모두 받았는지 확인하는 조건이야.

왜 이런 조건이 필요할까?

프로그램을 처음 실행하면 다음과 같은 상태일 수 있어.

```python
self.pose = None
self.color = None
self.velocity = None
```

이때 다음과 같은 코드가 실행되면 오류가 발생할 수 있어.

```python
self.velocity.linear.x
```

아직 `self.velocity`에 메시지가 저장되지 않았기 때문이야.

따라서 세 변수가 모두 `None`이 아닌 경우에만 출력하도록 만든 거야.

## 8-2. `self.velocity.linear.x` 이해하기

속도 메시지의 구조를 다시 보자.

```text
self.velocity
     │
     ▼
   Twist
     │
     ├── linear
     │     └── x
     │
     └── angular
           └── z
```

그래서 선속도를 확인할 때는 다음과 같이 작성해.

```python
self.velocity.linear.x
```

회전 속도를 확인할 때는 다음과 같이 작성해.

```python
self.velocity.angular.z
```

마치 객체 안에 있는 객체의 필드에 차례대로 접근하는 것과 같아.

Python에서는 이런 방식으로 중첩된 메시지의 값을 읽을 수 있어.

## 8-3. 출력 결과 이해하기

실행하면 다음과 비슷한 결과가 출력될 거야.

```text
[INFO] [lesson_04_pose_color_velocity_subscriber]:
위치: x=5.54, y=5.54, theta=0.00 |
색상: R=179, G=184, B=255 |
속도: linear.x=1.00, angular.z=0.50
```

실제 출력값은 실행 환경과 거북이 상태에 따라 달라져.

이 출력에서 확인할 수 있는 것은 다음과 같아.

- `x`, `y`: 거북이가 있는 위치
- `theta`: 거북이가 바라보는 방향
- `R`, `G`, `B`: 색상 센서의 RGB 값
- `linear.x`: 거북이에 전달된 앞뒤 방향 속도 명령
- `angular.z`: 거북이에 전달된 회전 속도 명령

다만 출력되는 위치와 속도 명령은 정확히 같은 시점의 값이라고 보장되지는 않아. 각각의 토픽 메시지가 도착하는 시점이 다르기 때문이야.

---

# 9. ROS 2에서 세 토픽을 직접 확인하는 방법

코드를 실행하기 전에 토픽 이름과 메시지 타입을 확인해 보면 좋아.

먼저 turtlesim을 실행해.

```bash
ros2 run turtlesim turtlesim_node
```

그다음 별도의 터미널에서 토픽 목록을 확인해.

```bash
ros2 topic list
```

세 토픽의 메시지 타입을 각각 확인하려면 다음 명령어를 실행해.

```bash
ros2 topic type /turtle1/pose
```

예상 결과:

```text
turtlesim/msg/Pose
```

색상 토픽:

```bash
ros2 topic type /turtle1/color_sensor
```

예상 결과:

```text
turtlesim/msg/Color
```

속도 토픽:

```bash
ros2 topic type /turtle1/cmd_vel
```

예상 결과:

```text
geometry_msgs/msg/Twist
```

이 명령어들은 코드에서 사용한 메시지 타입이 실제 토픽과 일치하는지 확인하는 데 유용해.

---

# 10. 이번 실습에서 꼭 알아야 할 차이

이번 코드에서 특히 기억하면 좋은 것은 **위치 정보와 속도 명령의 차이**야.

| 구분 | `/turtle1/pose` | `/turtle1/cmd_vel` |
|---|---|---|
| 의미 | 현재 위치와 상태 | 전달되는 속도 명령 |
| 메시지 타입 | `Pose` | `Twist` |
| 주요 필드 | `x`, `y`, `theta` | `linear.x`, `angular.z` |
| 주된 역할 | 현재 상태 확인 | 이동 명령 확인 |

예를 들어 `cmd_vel`에 `linear.x = 1.0`을 발행했다고 해서 거북이가 항상 정확히 1초 뒤에 특정 위치에 도착하는 것은 아니야.

거북이가 실제로 움직인 결과는 `/turtle1/pose`에서 확인할 수 있어.

이 개념은 나중에 실제 로봇을 다룰 때도 중요해.

- 명령을 발행하는 쪽은 로봇에 원하는 동작을 전달해.
- 상태를 구독하는 쪽은 로봇이 현재 어떤 상태인지 확인해.

둘을 구분해야 로봇이 명령대로 움직였는지 판단할 수 있어.

---

# 11. 마지막으로, 네가 직접 해 볼 실습

코드를 그대로 복사하는 것에서 한 단계 더 나아가 보자.

**실습 1.** 위치를 출력하는 코드에서 `theta`를 잠시 빼고 실행해 봐.

**실습 2.** 속도 출력에 다음 항목을 추가해 봐.

```python
self.velocity.linear.y
self.velocity.angular.x
self.velocity.angular.y
```

이 값들은 기본적인 2차원 turtlesim 이동에서 주로 사용하는 항목은 아니지만, `Twist` 메시지의 구조를 익히는 데 도움이 돼.

**실습 3.** 속도 명령을 발행한 뒤 위치가 실제로 어떻게 변하는지 관찰해 봐.

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

그리고 위치 토픽을 직접 확인해.

```bash
ros2 topic echo /turtle1/pose
```

명령으로 전달한 속도와 실제 위치 변화가 어떻게 연결되는지 확인할 수 있어.

이번 실습의 가장 중요한 개념은 세 가지야.

1. `create_subscription()`으로 여러 토픽을 동시에 구독할 수 있다.
2. 콜백 함수에서 각 메시지를 별도의 변수에 저장할 수 있다.
3. 타이머에서 저장된 데이터를 모아 함께 출력할 수 있다.

