
# 1. 이번 실습에서 무엇을 배우는 걸까?

먼저 turtlesim을 실행하면 화면에 거북이 한 마리가 나타나지?

ROS 2의 turtlesim은 거북이의 위치뿐만 아니라 거북이 아래에 있는 색상 센서의 RGB 값도 제공해.

이번에는 이 RGB 데이터를 구독해서 터미널에 출력하는 프로그램을 만드는 거야.

예를 들어 프로그램을 실행하면 다음과 같은 로그가 나올 수 있어.

```text
[INFO] [lesson_02_color_subscriber]: R: 69, G: 86, B: 255
[INFO] [lesson_02_color_subscriber]: R: 69, G: 86, B: 255
[INFO] [lesson_02_color_subscriber]: R: 69, G: 86, B: 255
```

숫자는 예시야. 실제 값은 거북이가 위치한 곳의 배경색에 따라 달라질 수 있어.

이번 실습의 목표는 크게 네 가지야.

1. ROS 2의 메시지 타입인 `Color` 이해하기
2. `create_subscription()`으로 토픽 구독하기
3. 콜백 함수에서 RGB 데이터 처리하기
4. `rclpy.spin()`으로 메시지를 계속 수신하기

먼저 전체적인 데이터 흐름부터 알아보자.

## ROS 2에서 데이터가 전달되는 과정

```text
┌──────────────────────┐
│   turtlesim_node     │
│                      │
│  색상 센서 데이터 생성  │
└──────────┬───────────┘
           │
           │ Publish
           ▼
┌─────────────────────────────┐
│ /turtle1/color_sensor       │
│                             │
│ 메시지 타입: turtlesim/msg/Color │
└──────────┬──────────────────┘
           │
           │ Subscribe
           ▼
┌─────────────────────────────┐
│     ColorSubscriber         │
│                             │
│  create_subscription()      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│       on_color()            │
│                             │
│ message.r                   │
│ message.g                   │
│ message.b                   │
└──────────┬──────────────────┘
           │
           ▼
       RGB 값 출력
```

여기서 반드시 기억할 개념이 있어.

**Publisher는 데이터를 발행하고, Subscriber는 데이터를 구독해서 받는다.**

Subscriber가 데이터를 직접 만들어 내는 것은 아니야. 다른 노드가 발행한 데이터를 받아서 처리하는 거지.

---

# 2. 코드 첫 부분부터 이해하기

먼저 네가 작성한 코드의 첫 부분을 보자.

```python
"""거북이 아래의 색상을 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Color
```

각 줄의 역할을 살펴보자.

### ① `import rclpy`

```python
import rclpy
```

`rclpy`는 Python에서 ROS 2를 사용하기 위한 라이브러리야.

ROS 2 프로그램에서 노드를 만들고 실행하려면 이 라이브러리가 필요해.

예를 들면 다음과 같은 기능을 사용할 수 있어.

| 코드 | 역할 |
|---|---|
| `rclpy.init()` | ROS 2 Python 클라이언트 초기화 |
| `rclpy.spin(node)` | 노드의 콜백을 계속 처리 |
| `rclpy.shutdown()` | ROS 2 종료 처리 |

즉, `rclpy`는 Python 프로그램이 ROS 2 시스템과 통신하도록 해 주는 도구라고 이해하면 돼.

### ② `from rclpy.node import Node`

```python
from rclpy.node import Node
```

여기서는 ROS 2의 `Node` 클래스를 가져와.

ROS 2에서 노드는 하나의 독립적인 기능을 수행하는 프로그램 단위야.

예를 들어 로봇 시스템에는 다음과 같은 노드가 있을 수 있어.

- 카메라 데이터를 발행하는 노드
- 라이다 데이터를 발행하는 노드
- 로봇의 위치를 추정하는 노드
- 모터를 제어하는 노드
- 센서 데이터를 구독하는 노드

이번 실습에서는 색상 센서 데이터를 구독하는 노드를 만들 거야.

다음 코드를 보면 이해하기 쉬워.

```python
class ColorSubscriber(Node):
```

이 문장은 `ColorSubscriber`라는 클래스를 정의하면서 `Node` 클래스를 상속받는다는 뜻이야.

쉽게 말하면 **ROS 2 노드가 갖고 있는 기본 기능을 물려받아 색상 구독 기능을 추가하는 것**이야.

Python의 클래스와 상속은 나중에 더 깊이 공부해도 괜찮아. 지금은 ROS 2 노드를 만들 때 이런 구조를 사용한다는 점부터 익히면 돼.

### ③ `from turtlesim.msg import Color`

```python
from turtlesim.msg import Color
```

이번 실습에서 중요한 부분이야.

이 코드는 turtlesim에서 사용하는 `Color` 메시지 타입을 가져오는 거야.

`Color` 메시지는 다음 세 가지 필드를 가지고 있어.

| 필드 | 의미 | 자료형 |
|---|---|---|
| `r` | Red, 빨간색 | 정수 |
| `g` | Green, 초록색 | 정수 |
| `b` | Blue, 파란색 | 정수 |

각 값은 0부터 255까지야.

예를 들어 다음과 같은 RGB 데이터가 있다고 해 보자.

```text
r = 255
g = 0
b = 0
```

이것은 빨간색을 나타내.

다른 예시도 살펴보자.

| RGB 값 | 색상 예시 |
|---|---|
| `(255, 0, 0)` | 빨간색 |
| `(0, 255, 0)` | 초록색 |
| `(0, 0, 255)` | 파란색 |
| `(255, 255, 255)` | 흰색 |
| `(0, 0, 0)` | 검은색 |

RGB는 빛의 삼원색을 이용해 색을 표현하는 방식이야.

다만 이번 실습에서는 RGB 값으로 실제 화면에 색을 그리는 것이 아니라, **센서에서 받은 RGB 숫자를 출력하는 것**이 목적이야.

---

# 3. 클래스와 생성자 이해하기

이제 다음 코드를 보자.

```python
class ColorSubscriber(Node):
    """RGB 색상을 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_02_color_subscriber')
```

여기서 중요한 것은 `__init__()`과 `super()`야.

## 3-1. `__init__()`은 무엇일까?

Python에서 `__init__()`은 객체를 생성할 때 초기화 작업을 수행하는 특별한 메서드야.

예를 들어 다음과 같이 작성했다고 해 보자.

```python
node = ColorSubscriber()
```

이렇게 `ColorSubscriber` 객체를 생성하면 `__init__()`이 실행돼.

따라서 이 메서드 안에 노드의 이름을 설정하거나 Subscriber를 생성하는 코드를 작성하는 거야.

## 3-2. `super().__init__()`은 무엇일까?

```python
super().__init__('lesson_02_color_subscriber')
```

이 코드는 부모 클래스인 `Node`의 초기화 기능을 호출해.

그리고 노드 이름으로 다음 문자열을 전달해.

```text
lesson_02_color_subscriber
```

여기서 주의할 점이 있어.

**노드 이름과 Python 클래스 이름은 서로 달라.**

| 구분 | 이름 |
|---|---|
| Python 클래스 이름 | `ColorSubscriber` |
| ROS 2 노드 이름 | `lesson_02_color_subscriber` |
| 실행 파일 이름 | `lesson_02_color_subscriber`로 설정할 예정 |

이름이 같을 수도 있지만, 세 가지는 서로 다른 개념이야.

특히 노드 이름은 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

정상적으로 실행 중이라면 다음과 비슷한 결과가 나와.

```text
/lesson_02_color_subscriber
/turtlesim
```

실제 출력은 실행 중인 노드에 따라 달라질 수 있어.

---

# 4. 핵심: `create_subscription()` 자세히 이해하기

이제 이번 실습에서 가장 중요한 부분을 살펴보자.

원래 코드에는 다음과 같은 주석이 있었어.

```python
# 실습 1: /turtlesim/color_sensor를 구독하세요.
# self.subscription =
```

이 부분을 다음과 같이 작성하면 돼.

```python
self.subscription = self.create_subscription(
    Color,
    '/turtle1/color_sensor',
    self.on_color,
    10
)
```

여기에는 네 가지 주요 인수가 들어가.

## 4-1. 전체 구조

```python
self.create_subscription(
    메시지_타입,
    토픽_이름,
    콜백_함수,
    QoS_큐_깊이
)
```

이 구조를 기억해 두면 앞으로 다른 토픽을 구독할 때도 활용할 수 있어.

각 항목을 하나씩 알아보자.

### 첫 번째: `Color`

```python
Color
```

Subscriber가 어떤 형태의 메시지를 받을지 지정하는 부분이야.

이번에는 RGB 데이터를 받으므로 `Color`를 사용해.

그런데 ROS 2에서 메시지 타입은 어떻게 확인할까?

먼저 turtlesim을 실행한 상태에서 다음 명령어를 입력해.

```bash
ros2 topic list
```

그러면 실행 중인 토픽 목록을 확인할 수 있어.

예를 들어 다음과 같은 목록이 나올 수 있어.

```text
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

여기서 `/turtle1/color_sensor`를 발견했다면 메시지 타입을 확인할 수 있어.

```bash
ros2 topic type /turtle1/color_sensor
```

예상 결과는 다음과 같아.

```text
turtlesim/msg/Color
```

이 결과가 Python 코드의 `Color`와 연결되는 거야.

조금 더 자세히 알아보려면 다음 명령어도 사용할 수 있어.

```bash
ros2 interface show turtlesim/msg/Color
```

메시지 정의를 확인하면 다음과 비슷한 내용을 볼 수 있어.

```text
uint8 r
uint8 g
uint8 b
```

여기서 `uint8`은 0부터 255까지의 정수를 표현할 수 있는 자료형이야.

이렇게 메시지 정의를 확인하면 어떤 필드를 사용할 수 있는지 알 수 있어.

### 두 번째: `'/turtle1/color_sensor'`

```python
'/turtle1/color_sensor'
```

이것은 구독할 토픽의 이름이야.

ROS 2에서 토픽은 노드끼리 메시지를 주고받는 통신 경로라고 생각하면 돼.

예를 들어 다음과 같은 토픽들이 있어.

| 토픽 | 데이터 |
|---|---|
| `/turtle1/cmd_vel` | 거북이의 이동 속도 명령 |
| `/turtle1/pose` | 거북이의 위치와 방향 |
| `/turtle1/color_sensor` | 거북이 아래 색상 센서의 RGB 값 |

여기서 한 가지 기억할 점이 있어.

`/turtle1/color_sensor`라는 이름은 네가 임의로 붙인 것이 아니라 turtlesim이 제공하는 토픽 이름이야.

그렇다면 왜 원래 주석에 있는 `/turtlesim/color_sensor`를 사용하지 않을까?

주석은 실습을 안내하기 위한 설명이지만, 실제 토픽 이름과 다를 수 있기 때문이야.

그래서 **토픽 이름이 확실하지 않을 때는 `ros2 topic list`로 실제 이름을 확인하는 습관**을 들이는 것이 좋아.

### 세 번째: `self.on_color`

```python
self.on_color
```

이 부분은 콜백 함수를 지정하는 곳이야.

콜백 함수란 특정 이벤트가 발생했을 때 호출되는 함수라고 이해하면 돼.

이번에는 색상 메시지가 도착했을 때 `on_color()`를 실행하도록 설정하는 거야.

여기서 주의할 점은 다음과 같아.

```python
self.on_color
```

이렇게 작성해야 해.

다음과 같이 괄호를 붙이면 안 돼.

```python
self.on_color()
```

왜냐하면 두 표현의 의미가 다르기 때문이야.

| 표현 | 의미 |
|---|---|
| `self.on_color` | 함수 자체를 전달 |
| `self.on_color()` | 함수를 즉시 호출 |

`create_subscription()`은 메시지가 도착할 때 실행할 함수를 등록해야 해.

따라서 함수 자체를 전달하는 `self.on_color`를 사용해야 하는 거야.

### 네 번째: `10`

```python
10
```

이 값은 QoS 설정의 큐 깊이야.

QoS는 Quality of Service의 약자로, ROS 2에서 메시지를 어떻게 전달하고 관리할지 정하는 설정이야.

여기서는 `10`이라는 값을 사용해 메시지 대기열의 깊이를 설정해.

초보 단계에서는 다음과 같이 기억하면 돼.

> `10`은 메시지를 처리하기 위해 사용하는 큐의 깊이를 지정하는 값이다.

단, ROS 2의 QoS는 큐 깊이 외에도 신뢰성이나 메시지 지속성 같은 여러 설정을 포함해. 이번 실습에서는 기본적인 구독 기능을 익히는 데 집중하자.

---

# 5. 콜백 함수에서 RGB 데이터 처리하기

이제 두 번째 실습 항목을 보자.

원래 코드는 다음과 같았어.

```python
def on_color(self, message):
    """수신한 색상을 처리합니다."""
    # 실습 2: message의 r, g, b를 출력하세요.
    pass
```

이 부분을 다음과 같이 수정하면 돼.

```python
def on_color(self, message):
    """수신한 색상을 처리합니다."""

    self.get_logger().info(
        f'R: {message.r}, G: {message.g}, B: {message.b}'
    )
```

이 코드도 하나씩 살펴보자.

## 5-1. `message`는 어디에서 오는 걸까?

```python
def on_color(self, message):
```

`message`는 Subscriber가 수신한 메시지 객체야.

앞에서 다음과 같이 구독을 등록했지?

```python
self.subscription = self.create_subscription(
    Color,
    '/turtle1/color_sensor',
    self.on_color,
    10
)
```

여기서 `Color` 타입의 메시지가 `/turtle1/color_sensor` 토픽으로 도착하면 ROS 2가 해당 메시지를 `on_color()`의 인수로 전달해.

따라서 `message` 안에 RGB 데이터가 들어 있게 돼.

예를 들어 메시지가 다음과 같다고 가정해 보자.

```text
r = 69
g = 86
b = 255
```

그러면 다음과 같이 접근할 수 있어.

```python
message.r
message.g
message.b
```

각각 `69`, `86`, `255`를 반환하는 거야.

이때 `message`는 우리가 임의로 만든 RGB 변수가 아니라, **ROS 2가 전달한 메시지 객체를 가리키는 변수**라는 점이 중요해.

## 5-2. `f'...'`는 무엇일까?

```python
f'R: {message.r}, G: {message.g}, B: {message.b}'
```

이것은 Python의 f-string이야.

문자열 안에 변수나 계산 결과를 넣을 때 사용해.

예를 들어 일반 문자열은 다음과 같아.

```python
print('R: message.r')
```

이렇게 작성하면 `message.r`이라는 글자 자체가 출력돼.

반면 다음과 같이 작성하면 실제 값이 출력돼.

```python
print(f'R: {message.r}')
```

만약 `message.r`이 `69`라면 다음과 같은 결과가 나와.

```text
R: 69
```

따라서 RGB 값을 한 줄로 출력하려면 다음처럼 작성할 수 있어.

```python
f'R: {message.r}, G: {message.g}, B: {message.b}'
```

## 5-3. `self.get_logger().info()`는 무엇일까?

```python
self.get_logger().info(
    f'R: {message.r}, G: {message.g}, B: {message.b}'
)
```

ROS 2의 로그 시스템을 사용해서 메시지를 출력하는 코드야.

Python의 `print()`와 비슷하지만, ROS 2 로그에는 메시지와 함께 로그 수준이나 시간 등의 정보가 포함될 수 있어.

대표적인 로그 함수는 다음과 같아.

| 함수 | 용도 |
|---|---|
| `self.get_logger().debug()` | 디버깅용 상세 정보 |
| `self.get_logger().info()` | 일반적인 정보 |
| `self.get_logger().warning()` | 주의가 필요한 상황 |
| `self.get_logger().error()` | 오류 상황 |
| `self.get_logger().fatal()` | 심각한 문제 |

이번 실습에서는 RGB 값을 확인하는 것이 목적이므로 `info()`를 사용해.

---

# 6. 마지막 실습: `rclpy.spin(node)`

원래 코드의 마지막 부분은 다음과 같았어.

```python
try:
    # 실습 3: node를 spin으로 실행하세요.
    pass
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

여기서 `pass` 부분을 다음과 같이 수정하면 돼.

```python
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

## 6-1. 왜 `spin()`이 필요할까?

Subscriber를 만들었다고 해서 프로그램이 자동으로 메시지를 계속 처리하는 것은 아니야.

ROS 2는 메시지가 도착했을 때 콜백을 실행할 수 있도록 이벤트를 처리해야 해.

`rclpy.spin(node)`는 노드가 종료되거나 중단될 때까지 실행되면서 콜백을 처리해.

예를 들어 다음과 같은 흐름이 반복되는 거야.

```text
rclpy.spin(node)
       │
       ▼
메시지 도착 확인
       │
       ▼
Color 메시지 수신
       │
       ▼
on_color(message) 실행
       │
       ▼
RGB 값 출력
       │
       ▼
다음 메시지 처리 대기
```

여기서 `spin()` 자체가 RGB 값을 출력하는 것은 아니야.

**`spin()`은 콜백이 실행될 수 있도록 노드를 계속 처리하고, 실제 RGB 출력은 `on_color()`가 담당해.**

## 6-2. `KeyboardInterrupt`는 무엇일까?

```python
except KeyboardInterrupt:
    pass
```

터미널에서 `Ctrl + C`를 누르면 일반적으로 Python 프로그램에 키보드 인터럽트가 발생해.

이 예외를 처리하면 사용자가 프로그램을 종료할 때 발생하는 예외를 의도된 종료 과정으로 다룰 수 있어.

## 6-3. `finally`는 무엇일까?

```python
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

`finally`는 예외 발생 여부와 관계없이 실행되는 정리 작업을 작성하는 곳이야.

- `node.destroy_node()`: 노드를 정리해.
- `rclpy.try_shutdown()`: ROS 2가 초기화된 상태라면 종료를 시도해.

이런 정리 작업은 ROS 2 프로그램을 깔끔하게 종료하는 데 도움이 돼.

---

# 7. 전체 코드 다시 확인하기

지금까지 배운 내용을 모두 합치면 다음과 같아.

```python
"""거북이 아래의 색상을 구독하는 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Color


class ColorSubscriber(Node):
    """RGB 색상을 출력하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_02_color_subscriber')

        # /turtle1/color_sensor 토픽 구독
        self.subscription = self.create_subscription(
            Color,
            '/turtle1/color_sensor',
            self.on_color,
            10
        )

    def on_color(self, message):
        """수신한 색상을 처리합니다."""

        self.get_logger().info(
            f'R: {message.r}, G: {message.g}, B: {message.b}'
        )


def main(args=None):
    """노드를 실행합니다."""

    rclpy.init(args=args)
    node = ColorSubscriber()

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

---

# 8. 실행 전에 알아둘 점

코드를 작성했더라도 패키지에 실행 파일이 등록되어 있어야 `ros2 run`으로 실행할 수 있어.

먼저 turtlesim을 실행해.

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

다른 터미널에서 토픽이 있는지 확인해.

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

그리고 메시지 타입을 확인해.

```bash
ros2 topic type /turtle1/color_sensor
```

예상 결과:

```text
turtlesim/msg/Color
```

이제 직접 작성한 노드를 실행할 수 있도록 패키지를 빌드해야 할 수도 있어.

```bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 다음을 실행해.

```bash
source install/setup.bash
ros2 run turtle_robot lesson_02_color_subscriber
```

이 명령어가 작동하려면 `setup.py`의 `console_scripts`에 `lesson_02_color_subscriber`가 등록되어 있어야 해.

---

# 9. 직접 확인해 보면 이해가 훨씬 빨라져

이번에는 코드를 실행하는 것뿐 아니라, 토픽에서 실제로 어떤 메시지가 전달되는지 확인해 보자.

turtlesim이 실행 중인 상태에서 다음 명령어를 입력해.

```bash
ros2 topic echo /turtle1/color_sensor
```

그러면 다음과 비슷한 데이터가 출력될 거야.

```yaml
r: 69
g: 86
b: 255
---
r: 69
g: 86
b: 255
---
```

이 명령어는 토픽의 메시지를 직접 확인하는 방법이야.

이후 네가 작성한 `ColorSubscriber`를 실행하면 같은 토픽의 데이터를 Python 코드로 받아 출력하게 되는 거지.

두 방법의 차이는 다음과 같아.

| 방법 | 역할 |
|---|---|
| `ros2 topic echo` | 터미널에서 토픽 메시지를 직접 확인 |
| `ColorSubscriber` | Python 프로그램에서 메시지를 받아 원하는 방식으로 처리 |

이 차이를 이해하면 ROS 2의 토픽 통신을 훨씬 쉽게 파악할 수 있어.

---

# 10. Lesson 01과 Lesson 02 비교하기

네가 이전에 공부한 Pose Subscriber와 비교해 보자.

| 항목 | Lesson 01: Pose Subscriber | Lesson 02: Color Subscriber |
|---|---|---|
| 메시지 타입 | `Pose` | `Color` |
| 토픽 | `/turtle1/pose` | `/turtle1/color_sensor` |
| 콜백 함수 | `on_pose()` | `on_color()` |
| 주요 데이터 | `x`, `y`, `theta` 등 | `r`, `g`, `b` |
| 공통 기능 | `create_subscription()` | `create_subscription()` |
| 공통 실행 방식 | `rclpy.spin(node)` | `rclpy.spin(node)` |

여기서 중요한 점은 **Subscriber의 기본 구조는 거의 같고, 메시지 타입과 토픽, 콜백에서 처리하는 데이터만 달라진다**는 거야.

이것이 ROS 2의 장점 중 하나야. 메시지 타입과 토픽을 이해하면 다양한 센서 데이터에도 같은 구조를 적용할 수 있어.

예를 들어 나중에 로봇을 공부할 때는 다음과 같은 데이터도 구독할 수 있어.

- 카메라 이미지
- 라이다 거리 데이터
- IMU의 가속도와 각속도
- 로봇의 위치와 자세
- 배터리 상태

물론 각 센서마다 사용하는 메시지 타입과 데이터 구조는 달라.

---

## 마지막으로, 꼭 기억할 핵심 4가지

1. **`Color`**는 RGB 데이터를 표현하는 ROS 2 메시지 타입이야.
2. **`create_subscription()`**은 특정 토픽을 구독하고 메시지가 도착하면 콜백을 실행하도록 등록해.
3. **`on_color(message)`**는 수신한 RGB 데이터를 처리하는 함수야.
4. **`rclpy.spin(node)`**는 노드가 메시지를 계속 처리할 수 있도록 실행 상태를 유지해.


