
# 1. 이번 실습에서 만들 프로그램

거북이 시뮬레이터인 `turtlesim`에는 거북이의 위치와 색상 정보를 제공하는 토픽이 있어.

이번에는 다음 두 토픽을 동시에 구독할 거야.

| 토픽 | 메시지 타입 | 전달하는 정보 |
|---|---|---|
| `/turtle1/pose` | `turtlesim/msg/Pose` | 거북이의 위치, 방향, 속도 |
| `/turtle1/color_sensor` | `turtlesim/msg/Color` | 거북이 아래에 있는 배경의 RGB 색상값 |

**주의:** 네 코드 주석에는 색상 토픽이 `/turtlesim/color_sensor`라고 적혀 있지만, 기본 turtlesim에서 사용하는 토픽 이름은 `/turtle1/color_sensor`야.

프로그램의 동작 흐름을 그림으로 표현하면 다음과 같아.

```text
              turtlesim
                  │
         ┌────────┴─────────┐
         │                  │
         ▼                  ▼
 /turtle1/pose      /turtle1/color_sensor
         │                  │
         ▼                  ▼
      on_pose()          on_color()
         │                  │
         ▼                  ▼
   self.pose 저장      self.color 저장
         │                  │
         └────────┬─────────┘
                  │
                  ▼
          print_values()
             1초마다
                  │
                  ▼
          위치와 색상 출력
```

핵심은 **두 콜백 함수가 받은 데이터를 각각 저장하고, 타이머가 저장된 데이터를 읽어서 출력한다는 것**이야.

---

# 2. 완성된 코드

먼저 전체 코드를 살펴보자.

```python
"""위치와 색상을 한 노드에서 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Color, Pose


class PoseColorSubscriber(Node):
    """위치와 색상을 함께 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_03_pose_color_subscriber')

        self.pose = None
        self.color = None

        # 실습 1: /turtle1/pose를 구독합니다.
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10
        )

        # 실습 2: /turtle1/color_sensor를 구독합니다.
        self.color_subscription = self.create_subscription(
            Color,
            '/turtle1/color_sensor',
            self.on_color,
            10
        )

        # 실습 3: print_values를 1초마다 실행합니다.
        self.timer = self.create_timer(
            1.0,
            self.print_values
        )

    def on_pose(self, message):
        """최근 위치를 저장합니다."""
        # 실습 4: 받은 Pose 메시지를 저장합니다.
        self.pose = message

    def on_color(self, message):
        """최근 색상을 저장합니다."""
        # 실습 5: 받은 Color 메시지를 저장합니다.
        self.color = message

    def print_values(self):
        """최근 위치와 색상을 출력합니다."""
        # 실습 6: 두 메시지를 모두 받았을 때 출력합니다.
        if self.pose is not None and self.color is not None:
            self.get_logger().info(
                f'위치: x={self.pose.x:.2f}, '
                f'y={self.pose.y:.2f}, '
                f'theta={self.pose.theta:.2f} | '
                f'색상: R={self.color.r}, '
                f'G={self.color.g}, '
                f'B={self.color.b}'
            )


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
```

이제 각 부분을 이해해 보자.

---

# 3. 클래스와 노드 생성

```python
class PoseColorSubscriber(Node):
```

여기서 `PoseColorSubscriber`는 우리가 직접 만든 클래스야.

괄호 안의 `Node`는 ROS 2에서 제공하는 노드 클래스야.

즉, 이 코드는 다음 의미야.

> ROS 2의 Node 기능을 상속받아 위치와 색상을 구독하는 새로운 노드를 만들겠다.

ROS 2에서는 노드가 실제 작업을 수행하는 기본 단위라고 생각하면 돼.

예를 들어 로봇 시스템에서는 다음처럼 역할을 나눌 수 있어.

- 카메라 노드: 카메라 영상 발행
- 위치 추정 노드: 로봇 위치 계산
- 이동 노드: 로봇의 속도 명령 발행
- 센서 구독 노드: 센서 데이터 수신

이번 실습에서는 하나의 노드가 위치와 색상 정보를 모두 받는 거야.

## `__init__()`은 무엇일까?

```python
def __init__(self):
    super().__init__('lesson_03_pose_color_subscriber')
```

`__init__()`은 객체를 생성할 때 실행되는 초기화 함수야.

`super().__init__(...)`은 부모 클래스인 `Node`의 초기화 기능을 호출해.

괄호 안의 문자열은 노드 이름이야.

따라서 이 노드의 이름은 다음과 같아.

```text
lesson_03_pose_color_subscriber
```

실행 후 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

출력 예시:

```text
/lesson_03_pose_color_subscriber
/turtlesim
```

실제 출력되는 노드 목록은 실행 중인 프로그램에 따라 달라질 수 있어.

---

# 4. `self.pose = None`과 `self.color = None`

```python
self.pose = None
self.color = None
```

이 두 줄은 이번 실습에서 매우 중요해.

## 4-1. `self`란?

`self`는 현재 객체 자신을 가리켜.

예를 들어 다음과 같이 작성하면,

```python
self.pose = None
```

현재 `PoseColorSubscriber` 객체 안에 `pose`라는 변수를 만든다는 뜻이야.

이 변수는 클래스 안의 다른 메서드에서도 접근할 수 있어.

## 4-2. `None`은 무엇일까?

`None`은 아직 값이 없다는 의미야.

프로그램을 처음 실행하면 위치 정보나 색상 정보를 아직 받지 못했을 수 있어.

따라서 다음과 같이 초기화하는 거야.

```python
self.pose = None
self.color = None
```

데이터를 받으면 값이 바뀌어.

```text
처음 실행
    │
    ├── self.pose = None
    └── self.color = None
             │
             ▼
위치 메시지 수신
    │
    └── self.pose = 위치 메시지
             │
             ▼
색상 메시지 수신
    │
    └── self.color = 색상 메시지
```

여기서 중요한 점은 **위치와 색상 메시지가 반드시 동시에 도착하는 것은 아니라는 것**이야.

그래서 아직 데이터를 받지 못한 상태를 `None`으로 구분하는 거야.

---

# 5. 실습 1: 위치 토픽 구독하기

```python
self.pose_subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

이 부분을 네 가지 항목으로 나누어 보자.

```python
self.create_subscription(
    메시지_타입,
    토픽_이름,
    콜백_함수,
    큐_크기
)
```

| 항목 | 코드 | 의미 |
|---|---|---|
| 메시지 타입 | `Pose` | 어떤 형태의 데이터를 받을 것인가? |
| 토픽 이름 | `'/turtle1/pose'` | 어느 토픽을 구독할 것인가? |
| 콜백 함수 | `self.on_pose` | 메시지가 도착하면 어떤 함수를 실행할 것인가? |
| 큐 크기 | `10` | 메시지 처리를 위한 대기열의 크기 |

## 5-1. `Pose`는 왜 사용할까?

```python
from turtlesim.msg import Color, Pose
```

여기서 `Pose`는 turtlesim에서 위치 정보를 전달하기 위해 정의한 메시지 타입이야.

`Pose` 메시지에는 다음과 같은 필드가 있어.

| 필드 | 의미 |
|---|---|
| `x` | 거북이의 X 좌표 |
| `y` | 거북이의 Y 좌표 |
| `theta` | 거북이가 바라보는 방향 |
| `linear_velocity` | 선형 속도 |
| `angular_velocity` | 각속도 |

예를 들어 다음과 같이 접근할 수 있어.

```python
self.pose.x
self.pose.y
self.pose.theta
```

단, `self.pose`가 실제 메시지를 받은 상태여야 이런 필드에 접근할 수 있어.

## 5-2. `self.on_pose`는 왜 괄호가 없을까?

```python
self.on_pose
```

이 부분은 꼭 이해해야 해.

다음 두 코드는 의미가 달라.

```python
self.on_pose
```

```python
self.on_pose()
```

첫 번째는 함수 자체를 전달하는 거야.

두 번째는 함수를 지금 즉시 실행하라는 뜻이야.

`create_subscription()`에는 메시지가 도착했을 때 실행할 함수를 전달해야 해.

그래서 다음처럼 작성해.

```python
self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

이렇게 등록해 놓으면 ROS 2가 해당 토픽의 메시지를 처리할 때 `on_pose()`를 호출해 줘.

---

# 6. 실습 2: 색상 토픽 구독하기

```python
self.color_subscription = self.create_subscription(
    Color,
    '/turtle1/color_sensor',
    self.on_color,
    10
)
```

위치 구독 코드와 거의 똑같아.

달라진 부분은 세 가지야.

```python
Color
'/turtle1/color_sensor'
self.on_color
```

이번에는 위치가 아니라 색상 메시지를 받는 거야.

## 6-1. 색상 메시지에는 무엇이 들어 있을까?

`Color` 메시지에는 다음 필드가 있어.

| 필드 | 의미 |
|---|---|
| `r` | 빨간색 값 |
| `g` | 초록색 값 |
| `b` | 파란색 값 |

각 필드의 값은 0부터 255 사이의 정수야.

예를 들어 다음과 같은 메시지를 받았다고 가정해 보자.

```text
r: 255
g: 0
b: 0
```

이 값은 빨간색을 의미해.

또 다음과 같은 값이라면,

```text
r: 0
g: 255
b: 0
```

초록색을 의미해.

다만 색상 센서는 **거북이 자체의 몸 색깔이 아니라 거북이가 위치한 배경의 색상값**을 제공해.

## 6-2. 실제 토픽 이름 확인하기

주석에는 다음과 같이 적혀 있었지.

```python
# /turtlesim/color_sensor
```

하지만 기본 turtlesim의 토픽 이름은 다음과 같아.

```text
/turtle1/color_sensor
```

실제로 확인하려면 turtlesim을 실행한 상태에서 터미널에 입력해 봐.

```bash
ros2 topic list
```

출력 목록에서 다음 두 토픽을 찾아보면 돼.

```text
/turtle1/pose
/turtle1/color_sensor
```

이렇게 확인하면 코드에 작성한 토픽 이름이 실제 시스템의 토픽 이름과 일치하는지 알 수 있어.

---

# 7. 실습 3: 타이머 만들기

```python
self.timer = self.create_timer(
    1.0,
    self.print_values
)
```

이 코드는 `print_values()` 함수를 1초마다 실행하도록 등록하는 부분이야.

형식은 다음과 같아.

```python
self.create_timer(시간_간격, 실행할_함수)
```

여기서:

```python
1.0
```

은 1초를 의미해.

```python
self.print_values
```

는 1초마다 실행할 함수야.

## 타이머가 왜 필요할까?

위치와 색상 토픽은 계속 메시지를 발행할 수 있어.

콜백 함수에서 매번 출력하면 터미널에 메시지가 너무 많이 쌓일 수 있지.

이번 실습에서는 메시지가 도착할 때마다 데이터를 저장하고, 출력은 1초마다 한 번만 하도록 설계한 거야.

```text
위치 메시지 ──→ self.pose 갱신
위치 메시지 ──→ self.pose 갱신
위치 메시지 ──→ self.pose 갱신

색상 메시지 ──→ self.color 갱신
색상 메시지 ──→ self.color 갱신

          타이머 실행
              │
              ▼
      print_values()
              │
              ▼
       최신 데이터 출력
```

**타이머는 메시지를 직접 받는 기능이 아니야.** 이미 저장된 데이터를 일정한 시간 간격으로 확인하는 기능이야.

---

# 8. 실습 4: 위치 메시지 저장하기

원래 코드에는 다음과 같이 작성되어 있어.

```python
def on_pose(self, message):
    """최근 위치를 저장합니다."""
    pass
```

여기서 `message`는 토픽을 통해 전달받은 메시지야.

완성 코드는 다음과 같아.

```python
def on_pose(self, message):
    """최근 위치를 저장합니다."""
    self.pose = message
```

이 한 줄이 어떤 의미인지 이해해 보자.

예를 들어 거북이가 다음 위치에 있다고 가정할게.

```text
x = 5.0
y = 6.0
theta = 1.57
```

ROS 2가 위치 메시지를 전달하면 `message` 안에 이 정보가 들어 있어.

```python
self.pose = message
```

이 코드는 전달받은 메시지를 `self.pose`에 저장하는 거야.

이제 다른 함수에서도 다음처럼 접근할 수 있어.

```python
self.pose.x
self.pose.y
self.pose.theta
```

여기서 `message`는 `on_pose()`가 호출될 때 전달되는 매개변수야.

반면 `self.pose`는 현재 객체에 저장해 두는 변수야.

| 이름 | 역할 |
|---|---|
| `message` | 이번에 전달받은 위치 메시지 |
| `self.pose` | 가장 최근에 저장해 둔 위치 메시지 |

참고로 이 코드는 메시지 객체 자체를 저장해. 이번 실습에서는 받은 메시지를 수정하지 않고 읽기만 하므로 이렇게 작성해도 괜찮아.

---

# 9. 실습 5: 색상 메시지 저장하기

색상도 같은 원리야.

완성 코드는 다음과 같아.

```python
def on_color(self, message):
    """최근 색상을 저장합니다."""
    self.color = message
```

색상 메시지를 받으면 `self.color`에 저장해.

예를 들어 메시지 내용이 다음과 같다고 가정해 보자.

```text
r = 179
g = 184
b = 255
```

그러면 다음과 같이 접근할 수 있어.

```python
self.color.r
self.color.g
self.color.b
```

여기서 중요한 것은 위치 메시지와 색상 메시지가 각각 다른 콜백 함수에서 저장된다는 점이야.

```python
def on_pose(self, message):
    self.pose = message

def on_color(self, message):
    self.color = message
```

두 함수는 독립적으로 실행되지만, 같은 객체에 저장된 데이터를 `print_values()`가 함께 사용할 수 있어.

---

# 10. 실습 6: 위치와 색상 출력하기

이제 마지막 부분이야.

```python
def print_values(self):
    """최근 위치와 색상을 출력합니다."""
    pass
```

우리는 위치와 색상을 모두 받은 경우에만 출력하려고 해.

## 10-1. 왜 `if`문이 필요할까?

프로그램을 처음 실행하면 다음과 같은 상태일 수 있어.

```python
self.pose = None
self.color = None
```

위치 메시지만 먼저 도착했다면 다음과 같겠지.

```python
self.pose = 위치 메시지
self.color = None
```

이 상태에서 아래와 같은 코드를 실행하면 문제가 생겨.

```python
self.color.r
```

`self.color`가 아직 `None`이기 때문에 `r` 필드를 읽을 수 없어.

그래서 두 메시지를 모두 받았는지 확인해야 해.

```python
if self.pose is not None and self.color is not None:
```

이 조건은 다음을 의미해.

- `self.pose is not None`: 위치 메시지를 받았는가?
- `self.color is not None`: 색상 메시지를 받았는가?
- `and`: 두 조건이 모두 참인가?

둘 다 참일 때만 아래의 출력 코드가 실행돼.

## 10-2. 실제 출력 코드

```python
self.get_logger().info(
    f'위치: x={self.pose.x:.2f}, '
    f'y={self.pose.y:.2f}, '
    f'theta={self.pose.theta:.2f} | '
    f'색상: R={self.color.r}, '
    f'G={self.color.g}, '
    f'B={self.color.b}'
)
```

처음 보면 조금 복잡해 보이지만, 문자열을 연결해서 출력하는 코드야.

### `self.get_logger().info()`

ROS 2에서 정보를 출력할 때 사용하는 로거야.

```python
self.get_logger().info('안녕하세요')
```

실행하면 다음과 비슷한 형태로 출력돼.

```text
[INFO] [시간] [lesson_03_pose_color_subscriber]: 안녕하세요
```

일반적인 Python의 `print()`와 비슷한 용도로 사용하지만, ROS 2의 로거는 메시지의 심각도와 노드 이름 등을 함께 표시해 줘.

### `f'...'`는 무엇일까?

문자열 앞의 `f`는 f-string이라는 Python 기능이야.

문자열 안에 변수의 값을 넣을 수 있어.

예를 들어:

```python
x = 5.12345

print(f'x={x}')
```

출력:

```text
x=5.12345
```

이번 코드에서는 다음과 같이 사용하고 있어.

```python
f'x={self.pose.x:.2f}'
```

여기서 `:.2f`는 숫자를 소수점 둘째 자리까지 표시하라는 뜻이야.

예를 들어 값이 `5.12345`라면 다음처럼 출력돼.

```text
x=5.12
```

`theta`에도 같은 형식을 사용했어.

색상값은 정수이기 때문에 소수점 형식을 지정하지 않았어.

### 출력 예시

실행하면 대략 다음과 같은 결과를 볼 수 있어.

```text
[INFO] [lesson_03_pose_color_subscriber]: 위치: x=5.54, y=5.54, theta=0.00 | 색상: R=179, G=184, B=255
[INFO] [lesson_03_pose_color_subscriber]: 위치: x=5.54, y=5.54, theta=0.00 | 색상: R=179, G=184, B=255
[INFO] [lesson_03_pose_color_subscriber]: 위치: x=5.54, y=5.54, theta=0.00 | 색상: R=179, G=184, B=255
```

위 값들은 출력 형식을 보여 주기 위한 예시야. 실제 값은 거북이의 위치와 주변 배경색에 따라 달라져.

거북이가 움직이지 않는다면 위치가 계속 같을 수도 있어.

---

# 11. `main()` 함수 이해하기

코드 마지막 부분도 살펴보자.

```python
def main(args=None):
    rclpy.init(args=args)
    node = PoseColorSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
```

### ① ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 프로그램을 실행하기 위한 초기화 과정이야.

### ② 노드 생성

```python
node = PoseColorSubscriber()
```

앞에서 작성한 클래스로 실제 노드 객체를 만드는 거야.

이때 `__init__()`이 실행되면서 다음 작업이 등록돼.

- 위치 토픽 구독
- 색상 토픽 구독
- 1초 타이머 생성

### ③ 노드 실행 유지

```python
rclpy.spin(node)
```

이 부분도 매우 중요해.

`spin()`은 노드가 메시지를 처리하고 콜백 함수를 실행할 수 있도록 유지해 줘.

이 코드가 없으면 프로그램이 종료되거나 콜백 처리가 제대로 이루어지지 않을 수 있어.

### ④ 종료 처리

```python
except KeyboardInterrupt:
    pass
```

터미널에서 `Ctrl + C`를 눌러 종료할 때 발생하는 키보드 인터럽트를 처리해.

```python
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

노드를 정리하고 ROS 2를 종료하는 과정이야.

---

# 12. 실제로 실행해 보기

이제 코드를 작성했다면 실행해 보자.

Ubuntu에서 터미널을 세 개 사용하면 편해.

## 터미널 1: turtlesim 실행

ROS 2 Jazzy를 설치한 환경이라면 먼저 다음을 실행해.

```bash
source /opt/ros/jazzy/setup.bash
```

그다음:

```bash
ros2 run turtlesim turtlesim_node
```

거북이 시뮬레이터 창이 나타나면 성공이야.

## 터미널 2: 실습 코드 실행

네 ROS 2 워크스페이스가 `~/ros2_ws`라면 다음 순서로 실행해.

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run turtle_robot lesson_03_pose_color_subscriber
```

마지막 명령어는 `turtle_robot` 패키지의 실행 파일 이름이 `lesson_03_pose_color_subscriber`로 등록되어 있다는 전제야.

만약 실행 파일을 찾지 못한다는 오류가 발생하면 `setup.py`의 `console_scripts` 등록 여부를 확인해야 해.

코드를 수정한 뒤에는 패키지를 다시 빌드해야 할 수도 있어.

```bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
source install/setup.bash
```

## 터미널 3: 토픽 확인

다음 명령어를 실행해 봐.

```bash
ros2 topic list
```

그리고 위치 토픽의 메시지 타입을 확인하려면:

```bash
ros2 topic type /turtle1/pose
```

예상 결과:

```text
turtlesim/msg/Pose
```

색상 토픽도 확인해 보자.

```bash
ros2 topic type /turtle1/color_sensor
```

예상 결과:

```text
turtlesim/msg/Color
```

이렇게 확인하면 네 코드에서 사용한 메시지 타입이 실제 토픽의 타입과 일치하는지 검증할 수 있어.

---

# 13. 이번 실습에서 꼭 기억할 개념 5가지

| 개념 | 기억해야 할 내용 |
|---|---|
| `create_subscription()` | 특정 토픽을 구독하고 콜백 함수를 등록한다. |
| `message` | 콜백 함수에 전달되는 메시지 데이터다. |
| `self.pose`, `self.color` | 가장 최근에 받은 메시지를 저장한다. |
| `create_timer()` | 지정된 시간 간격으로 함수를 실행한다. |
| `self.get_logger().info()` | ROS 2 로거를 이용해 정보를 출력한다. |

이번 실습의 핵심을 한 문장으로 정리하면 다음과 같아.

**위치와 색상 메시지는 각각의 콜백 함수에서 저장하고, 타이머는 저장된 최신 데이터를 1초마다 출력한다.**

