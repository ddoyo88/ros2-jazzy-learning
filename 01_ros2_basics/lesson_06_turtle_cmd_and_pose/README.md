
# 1. 프로그램 전체 동작 이해하기

먼저 프로그램이 어떻게 동작하는지 살펴보자.

```text
┌────────────────────────────┐
│ turtlesim                  │
│                            │
│ 거북이 위치와 방향 계산     │
└─────────────┬──────────────┘
              │
              │ /turtle1/pose
              ▼
┌────────────────────────────┐
│ Subscriber                 │
│                            │
│ on_pose()                  │
│ 최신 위치 저장              │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ publish_velocity()         │
│                            │
│ 1. 현재 위치 확인           │
│ 2. 방향 계산                │
│ 3. 벽을 향하는지 판단       │
└─────────────┬──────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   벽을 향함       벽을 향하지 않음
       │             │
       ▼             ▼
   회전 명령       직진 명령
       │             │
       └──────┬──────┘
              │
              ▼
┌────────────────────────────┐
│ Publisher                  │
│ /turtle1/cmd_vel            │
└─────────────┬──────────────┘
              │
              ▼
       turtlesim 거북이 이동
```

핵심은 **위치를 확인하고 → 상황을 판단하고 → 속도 명령을 보내는 것**이야.

이러한 구조는 실제 로봇에서도 자주 사용해.

예를 들어 이동 로봇이 센서로 주변 환경을 파악하고, 자신의 위치를 확인한 다음, 이동할 방향과 속도를 결정하는 방식과 비슷해.

다만 이번 프로그램은 실제 거리 센서를 사용하는 것은 아니야. 거북이의 위치와 방향을 이용해서 벽에 접근하는 상황을 추정하는 간단한 제어 프로그램이야.

---

# 2. 라이브러리 가져오기

먼저 코드 상단을 살펴보자.

```python
import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
```

각 라이브러리의 역할은 다음과 같아.

| 코드 | 역할 |
|---|---|
| `import math` | 삼각함수와 수학 연산 사용 |
| `Twist` | 이동 속도와 회전 속도를 표현 |
| `rclpy` | ROS 2 Python 기능 사용 |
| `Node` | ROS 2 노드 생성 |
| `Pose` | 거북이의 위치와 방향 정보 수신 |

이번 코드에서는 특히 `math`와 `Pose`를 잘 이해해야 해.

## 2-1. `math`

```python
import math
```

Python에서 수학 함수를 사용하기 위한 라이브러리야.

이번 코드에서는 다음 두 함수를 사용해.

```python
math.cos()
math.sin()
```

이 함수들은 거북이가 바라보는 방향을 x축과 y축 방향의 값으로 변환하는 데 사용해.

뒤에서 자세히 설명할게.

## 2-2. `Twist`

```python
from geometry_msgs.msg import Twist
```

거북이에게 이동 명령을 전달하기 위한 메시지 타입이야.

예를 들어 다음과 같이 사용할 수 있어.

```python
msg = Twist()

msg.linear.x = 1.0
msg.angular.z = 0.0
```

이 명령은 거북이가 앞으로 이동하고 회전하지 않도록 해.

반대로 다음과 같이 작성하면 회전하게 돼.

```python
msg = Twist()

msg.linear.x = 0.0
msg.angular.z = 1.5
```

이 경우 직선 이동 속도는 0이고 회전 속도만 1.5로 설정돼.

## 2-3. `Pose`

```python
from turtlesim.msg import Pose
```

`Pose`는 turtlesim 거북이의 현재 위치와 방향을 나타내는 메시지 타입이야.

주요 필드는 다음과 같아.

| 필드 | 의미 | 예시 |
|---|---|---:|
| `x` | 현재 x 좌표 | 5.0 |
| `y` | 현재 y 좌표 | 5.0 |
| `theta` | 현재 방향 각도 | 1.57 |
| `linear_velocity` | 현재 선속도 | 1.0 |
| `angular_velocity` | 현재 각속도 | 0.0 |

예를 들어 다음과 같은 위치 메시지를 받았다고 가정해 보자.

```text
x = 5.0
y = 5.0
theta = 0.0
```

이것은 거북이가 화면 좌표 `(5.0, 5.0)`에 있고, 방향 각도가 0이라는 뜻이야.

turtlesim에서는 방향 각도에 따라 거북이가 향하는 방향을 알 수 있어.

---

# 3. TurtleCmdAndPose 클래스

```python
class TurtleCmdAndPose(Node):
    """속도를 발행하고 위치를 구독하는 노드입니다."""
```

이 코드는 `TurtleCmdAndPose`라는 ROS 2 노드를 정의해.

이전 실습에서는 속도를 발행하는 기능이 중심이었어.

이번에는 두 가지 기능을 동시에 수행해.

- Publisher: 속도 명령 발행
- Subscriber: 거북이 위치 수신

즉, 명령만 보내는 것이 아니라 거북이의 상태도 확인할 수 있게 된 거야.

이런 구조는 로봇 제어에서 매우 중요해.

예를 들어 실제 자율주행 로봇도 단순히 앞으로 가라는 명령만 반복해서 보내는 것이 아니라, 센서와 위치 추정 결과를 확인하면서 움직임을 조정해야 해.

---

# 4. 노드 초기화

```python
def __init__(self):
    super().__init__('lesson_06_turtle_cmd_and_pose')
    self.pose = None
```

## 4-1. 노드 이름 설정

```python
super().__init__('lesson_06_turtle_cmd_and_pose')
```

부모 클래스인 `Node`를 초기화하면서 노드 이름을 설정하는 코드야.

노드 이름은 다음과 같아.

```text
lesson_06_turtle_cmd_and_pose
```

실행 중인 노드는 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

## 4-2. `self.pose = None`

```python
self.pose = None
```

이 부분은 아주 중요해.

`self.pose`는 거북이의 최신 위치 정보를 저장하는 변수야.

그런데 노드가 처음 실행될 때는 아직 위치 메시지를 받지 못했을 수 있어.

따라서 처음에는 다음과 같이 설정하는 거야.

```python
self.pose = None
```

여기서 `None`은 아직 값이 없다는 의미야.

이후 위치 메시지가 도착하면 다음 코드에서 실제 값으로 바뀌어.

```python
self.pose = message
```

예를 들어 처음에는 다음과 같아.

```python
self.pose = None
```

위치 메시지를 받으면 다음과 같이 사용할 수 있게 돼.

```python
self.pose.x
self.pose.y
self.pose.theta
```

**왜 처음부터 좌표를 0으로 설정하지 않을까?**

다음과 같이 작성할 수도 있겠지.

```python
self.x = 0.0
self.y = 0.0
```

하지만 실제 위치 메시지를 받기 전에는 이 값들이 실제 거북이의 위치라고 보장할 수 없어.

그래서 이번 실습에서는 아직 위치를 받지 못했다는 사실을 `None`으로 구분하는 거야.

---

# 5. Publisher 생성하기

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

이 코드는 거북이에게 속도 명령을 보내기 위한 Publisher를 생성해.

각 인자의 의미를 살펴보자.

| 인자 | 의미 |
|---|---|
| `Twist` | 발행할 메시지 타입 |
| `'/turtle1/cmd_vel'` | 발행할 토픽 이름 |
| `10` | QoS 큐 깊이 |

이번에는 `/turtle1/cmd_vel`이라는 토픽에 속도 명령을 발행해.

전체 통신 구조는 다음과 같아.

```text
lesson_06_turtle_cmd_and_pose
              │
              │ Twist 발행
              ▼
     /turtle1/cmd_vel
              │
              ▼
          turtlesim
              │
              ▼
           거북이
```

이 코드는 Publisher를 생성할 뿐, 아직 속도 명령을 보내지는 않아.

실제 발행은 나중에 다음 코드에서 수행해.

```python
self.publisher.publish(msg)
```

---

# 6. Subscriber 생성하기

```python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

이 부분은 Publisher만큼 중요해.

이번에는 거북이의 위치 정보를 받기 위한 Subscriber를 생성해.

각 인자를 살펴보자.

| 인자 | 의미 |
|---|---|
| `Pose` | 수신할 메시지 타입 |
| `'/turtle1/pose'` | 구독할 토픽 이름 |
| `self.on_pose` | 메시지를 받았을 때 실행할 함수 |
| `10` | QoS 큐 깊이 |

여기서 핵심은 세 번째 인자야.

```python
self.on_pose
```

이것은 `on_pose()` 함수를 실행하라는 의미가 아니라, **메시지가 도착했을 때 호출할 함수 자체를 전달하는 것**이야.

괄호가 없다는 점에 주목해.

```python
self.on_pose
```

이렇게 작성해야 ROS 2가 나중에 해당 함수를 호출할 수 있어.

반면 다음과 같이 작성하면 함수가 즉시 호출되므로 의도한 사용법이 아니야.

```python
self.on_pose()
```

## Publisher와 Subscriber 비교

이번 코드에는 두 가지 통신 기능이 있어.

| 구분 | Publisher | Subscriber |
|---|---|---|
| 역할 | 속도 명령 발행 | 위치 정보 수신 |
| 메시지 타입 | `Twist` | `Pose` |
| 토픽 | `/turtle1/cmd_vel` | `/turtle1/pose` |
| 주요 코드 | `publish(msg)` | `on_pose(message)` |

정리하면 다음과 같아.

```text
/turtle1/pose
      │
      │ Pose 메시지 수신
      ▼
  on_pose()
      │
      ▼
 self.pose에 저장
      │
      ▼
위치와 방향 분석
      │
      ▼
/turtle1/cmd_vel
      │
      │ Twist 메시지 발행
      ▼
   turtlesim
```

이제 거북이의 현재 상태를 확인하면서 이동 명령을 만들 수 있어.

---

# 7. Timer 생성하기

```python
self.timer = self.create_timer(
    0.1,
    self.publish_velocity
)
```

이 코드는 약 0.1초마다 `publish_velocity()` 함수를 실행하도록 해.

계산하면 다음과 같아.

```text
1초 ÷ 0.1초 = 초당 약 10회
```

따라서 프로그램은 약 0.1초마다 거북이의 위치를 확인하고, 이동 방향을 판단한 다음, 속도 명령을 발행하게 돼.

여기서 중요한 점이 있어.

**타이머가 실행될 때마다 위치 정보를 새로 요청하는 것은 아니야.**

위치 정보는 Subscriber가 별도로 수신해.

타이머는 `self.pose`에 저장된 최신 위치 정보를 사용해.

예를 들어 다음과 같은 상황이야.

```text
시간 0.0초: 위치 메시지 수신 → self.pose 저장
시간 0.1초: publish_velocity() → 저장된 위치 사용
시간 0.2초: publish_velocity() → 최신 위치 사용
시간 0.3초: 위치 메시지 수신 → self.pose 갱신
시간 0.4초: publish_velocity() → 갱신된 위치 사용
```

실제 메시지 수신과 타이머 실행의 순서는 상황에 따라 달라질 수 있지만, 기본적인 구조는 이와 같아.

---

# 8. 위치 메시지를 처리하는 `on_pose()`

이제 위치 정보를 저장하는 부분을 보자.

```python
def on_pose(self, message):
    """최근 위치를 저장합니다."""

    self.pose = message
```

이 함수는 `/turtle1/pose` 토픽에서 위치 메시지가 도착하면 실행돼.

## 8-1. `message`는 무엇일까?

```python
def on_pose(self, message):
```

`message`는 Subscriber가 수신한 `Pose` 메시지 객체야.

예를 들어 다음과 같은 데이터를 받았다고 해 보자.

```text
x = 5.0
y = 6.0
theta = 1.57
linear_velocity = 1.0
angular_velocity = 0.0
```

그러면 `message`를 통해 각 필드에 접근할 수 있어.

```python
message.x
message.y
message.theta
```

## 8-2. 위치 저장

```python
self.pose = message
```

수신한 메시지를 `self.pose`에 저장해.

이후 다른 함수에서도 해당 위치 정보를 사용할 수 있어.

예를 들어 다음과 같이 작성할 수 있지.

```python
p = self.pose

print(p.x)
print(p.y)
print(p.theta)
```

여기서 `p`는 `self.pose`에 저장된 메시지를 가리켜.

따라서 다음 두 표현은 같은 위치 정보를 참조해.

```python
self.pose.x
```

```python
p.x
```

이 코드는 단순하지만 중요한 역할을 해.

**Subscriber가 위치를 저장하고, Timer가 저장된 위치를 사용해 판단하는 구조**를 만들어 주기 때문이야.

---

# 9. `publish_velocity()` 함수 시작 부분

```python
def publish_velocity(self):
    """벽을 피하는 속도를 발행합니다."""

    if self.pose is None:
        return

    p = self.pose
```

이제 실제로 벽을 피하는 동작을 만드는 부분이야.

## 9-1. `if self.pose is None`

```python
if self.pose is None:
    return
```

이 코드는 아직 위치 메시지를 받지 못했는지 확인해.

노드가 처음 실행되었을 때는 다음과 같을 수 있어.

```python
self.pose = None
```

이 상태에서 다음과 같은 코드를 실행하면 문제가 생겨.

```python
p = self.pose
print(p.x)
```

`p`가 `None`이므로 `p.x`에 접근할 수 없기 때문이야.

따라서 먼저 확인하는 거야.

```python
if self.pose is None:
    return
```

뜻은 다음과 같아.

> 아직 위치 정보가 없다면 이번 함수 실행을 여기서 끝내라.

여기서 `return`은 함수 실행을 종료한다는 의미야.

위치 정보가 없으면 이동 명령을 발행하지 않고, 위치 정보가 들어온 다음 타이머가 다시 실행될 때 판단을 시작해.

## 9-2. `p = self.pose`

```python
p = self.pose
```

이 코드는 위치 메시지를 간단한 변수 이름인 `p`로 참조하기 위한 거야.

따라서 이후에 다음과 같이 사용할 수 있어.

```python
p.x
p.y
p.theta
```

굳이 긴 `self.pose`를 반복해서 쓰지 않아도 돼.

---

# 10. 가장 중요한 수학: 거북이가 향하는 방향 계산하기

이제 다음 두 줄을 보자.

```python
dx = math.cos(p.theta)
dy = math.sin(p.theta)
```

처음에는 어렵게 느껴질 수 있지만, 원리를 이해하면 간단해.

먼저 거북이가 방향을 가지고 있다는 사실을 생각해 보자.

거북이는 화면에서 다음과 같은 방향을 바라볼 수 있어.

- 오른쪽
- 위쪽
- 왼쪽
- 아래쪽

또한 중간 방향도 가능해.

예를 들어 오른쪽 위를 향할 수도 있어.

이번 프로그램에서는 거북이가 바라보는 방향을 `theta`라는 각도로 표현해.

## 10-1. `theta`란?

```python
p.theta
```

`theta`는 그리스 문자 θ를 의미하며, 거북이가 바라보는 방향을 나타내는 각도야.

turtlesim에서는 각도를 라디안 단위로 사용해.

대표적인 각도는 다음과 같아.

| 방향 | `theta` 값 |
|---|---:|
| 오른쪽 | 0 |
| 위쪽 | 약 1.57 |
| 왼쪽 | 약 3.14 |
| 아래쪽 | 약 -1.57 |
| 오른쪽으로 한 바퀴 회전한 방향 | 약 6.28 |

여기서 1.57은 약 90도이고, 3.14는 약 180도야.

라디안과 도의 관계는 다음과 같아.

\[
180^\circ = \pi \text{ rad}
\]

따라서 다음과 같이 이해하면 돼.

\[
90^\circ = \frac{\pi}{2} \approx 1.57
\]

중요한 것은 `theta`가 위치가 아니라 **방향을 나타내는 값**이라는 점이야.

---

## 10-2. 왜 `cos()`를 사용할까?

```python
dx = math.cos(p.theta)
```

이 코드는 거북이가 향하는 방향의 x축 성분을 계산해.

예를 들어 거북이가 오른쪽을 향한다고 가정해 보자.

```python
p.theta = 0.0
```

그러면 다음과 같아.

\[
dx = \cos(0) = 1
\]

즉, `dx`는 1이 돼.

이것은 거북이가 x축의 양의 방향, 즉 오른쪽을 향하고 있다는 의미야.

다른 방향도 살펴보자.

| 방향 | `theta` | `cos(theta)` | x축 방향 |
|---|---:|---:|---|
| 오른쪽 | 0 | 1 | 오른쪽 |
| 위쪽 | 약 1.57 | 약 0 | 거의 수평 이동 없음 |
| 왼쪽 | 약 3.14 | -1 | 왼쪽 |
| 아래쪽 | 약 -1.57 | 약 0 | 거의 수평 이동 없음 |

여기서 `dx`의 의미를 기억해.

- `dx > 0`: x축의 양의 방향을 향함
- `dx < 0`: x축의 음의 방향을 향함
- `dx`가 0에 가까움: 수평 방향 성분이 거의 없음

즉, `dx`는 거북이가 어느 쪽으로 이동하려는지를 판단하는 데 사용할 수 있어.

## 10-3. 왜 `sin()`을 사용할까?

```python
dy = math.sin(p.theta)
```

이번에는 y축 방향 성분을 계산해.

예를 들어 거북이가 위쪽을 향한다고 가정해 보자.

```python
p.theta = 1.5708
```

그러면 다음과 같아.

\[
dy = \sin(1.5708) \approx 1
\]

따라서 `dy`는 약 1이 돼.

다른 방향도 살펴보자.

| 방향 | `theta` | `sin(theta)` | y축 방향 |
|---|---:|---:|---|
| 오른쪽 | 0 | 0 | 수직 방향 성분 없음 |
| 위쪽 | 약 1.57 | 1 | 위쪽 |
| 왼쪽 | 약 3.14 | 약 0 | 수직 방향 성분 없음 |
| 아래쪽 | 약 -1.57 | -1 | 아래쪽 |

따라서 `dy`는 거북이가 y축의 어느 방향을 향하는지 판단하는 데 사용할 수 있어.

### `dx`와 `dy`를 함께 이해하기

이제 두 코드를 다시 보자.

```python
dx = math.cos(p.theta)
dy = math.sin(p.theta)
```

두 값을 함께 사용하면 거북이가 향하는 방향을 x축과 y축 성분으로 표현할 수 있어.

예를 들어 다음과 같아.

| 거북이 방향 | `dx` | `dy` |
|---|---:|---:|
| 오른쪽 | 1 | 0 |
| 위쪽 | 0 | 1 |
| 왼쪽 | -1 | 0 |
| 아래쪽 | 0 | -1 |
| 오른쪽 위 대각선 | 약 0.707 | 약 0.707 |

오른쪽 위를 향하는 경우에는 x축과 y축 방향으로 모두 양의 성분이 나타나.

이 값들을 이용하면 거북이가 어느 방향으로 이동하려는지 계산할 수 있어.

**여기서 중요한 점:** `dx`와 `dy`는 실제 이동 거리가 아니야. 거북이가 향하는 방향을 x축과 y축으로 나누어 나타낸 값이야.

---

# 11. 벽을 향하고 있는지 판단하기

이번 실습의 핵심 코드야.

```python
toward_wall = (
    (p.x < 1.5 and dx < 0)
    or (p.x > 9.5 and dx > 0)
    or (p.y < 1.5 and dy < 0)
    or (p.y > 9.5 and dy > 0)
)
```

처음에는 복잡해 보이지만, 네 가지 상황을 검사하는 코드야.

turtlesim의 기본 화면 좌표는 대략 x와 y가 0부터 11까지인 범위로 생각할 수 있어.

거북이는 화면 경계를 통과할 수 없으므로, 여기서는 경계에 너무 가까워지기 전에 방향을 바꾸도록 하고 있어.

코드에서는 `1.5`와 `9.5`를 기준으로 삼고 있어.

즉, 화면의 바깥쪽 경계에 가까운 영역을 벽 근처라고 간주하는 거야.

## 11-1. 첫 번째 조건

```python
(p.x < 1.5 and dx < 0)
```

이 조건은 두 가지를 확인해.

1. 거북이의 x 좌표가 1.5보다 작은가?
2. 거북이가 왼쪽 방향을 향하고 있는가?

두 조건이 모두 참이면 `True`가 돼.

예를 들어 다음과 같은 상황을 생각해 보자.

```python
p.x = 1.0
dx = -1.0
```

거북이는 화면 왼쪽에 가까이 있고, 왼쪽을 향하고 있어.

따라서 왼쪽 벽을 향해 이동하려는 상황이라고 판단해.

반대로 다음과 같다면 어떨까?

```python
p.x = 1.0
dx = 1.0
```

거북이는 왼쪽에 가깝지만 오른쪽을 향하고 있어.

따라서 왼쪽 벽으로 접근하는 상황이 아니므로 이 조건은 `False`야.

**벽과의 거리만 보는 것이 아니라, 벽 쪽으로 이동하려는 방향인지도 확인한다는 점이 중요해.**

## 11-2. 두 번째 조건

```python
(p.x > 9.5 and dx > 0)
```

이번에는 오른쪽 벽을 확인해.

두 가지 조건이 있어.

- x 좌표가 9.5보다 큰가?
- 거북이가 오른쪽 방향을 향하고 있는가?

예를 들어 다음과 같다면 오른쪽 벽을 향하고 있는 것으로 판단해.

```python
p.x = 10.0
dx = 1.0
```

하지만 다음과 같다면 벽 쪽으로 향하고 있지 않아.

```python
p.x = 10.0
dx = -1.0
```

거북이가 화면 오른쪽에 있지만 왼쪽을 향하고 있기 때문이야.

## 11-3. 세 번째 조건

```python
(p.y < 1.5 and dy < 0)
```

이번에는 y 좌표를 확인해.

- y 좌표가 1.5보다 작은가?
- 거북이가 y축의 음의 방향을 향하고 있는가?

둘 다 참이면 아래쪽 벽을 향하고 있다고 판단해.

예를 들어 다음과 같아.

```python
p.y = 1.0
dy = -1.0
```

거북이가 아래쪽 벽에 가까이 있고 아래쪽을 향하고 있으므로 회전이 필요하다고 판단하는 거야.

## 11-4. 네 번째 조건

```python
(p.y > 9.5 and dy > 0)
```

이번에는 위쪽 벽을 확인해.

- y 좌표가 9.5보다 큰가?
- 거북이가 y축의 양의 방향을 향하고 있는가?

예를 들어 다음과 같아.

```python
p.y = 10.0
dy = 1.0
```

거북이가 위쪽 벽에 가까이 있고 위쪽을 향하고 있으므로 이 조건은 참이야.

---

# 12. `and`와 `or` 이해하기

이 조건문을 이해하려면 Python의 논리 연산자를 알아야 해.

```python
toward_wall = (
    (p.x < 1.5 and dx < 0)
    or (p.x > 9.5 and dx > 0)
    or (p.y < 1.5 and dy < 0)
    or (p.y > 9.5 and dy > 0)
)
```

여기서 사용한 연산자는 두 가지야.

### `and`

두 조건이 모두 참이어야 전체 결과가 참이야.

예를 들어 다음과 같아.

```python
p.x < 1.5 and dx < 0
```

| `p.x < 1.5` | `dx < 0` | 결과 |
|---|---|---|
| 참 | 참 | 참 |
| 참 | 거짓 | 거짓 |
| 거짓 | 참 | 거짓 |
| 거짓 | 거짓 | 거짓 |

### `or`

여러 조건 중 하나라도 참이면 전체 결과가 참이야.

이번 코드에서는 네 방향 중 하나라도 벽을 향하는 상황이면 회전하도록 해.

```python
조건1 or 조건2 or 조건3 or 조건4
```

예를 들어 다음과 같다고 가정해 보자.

```python
p.x = 1.0
dx = -1.0

p.y = 5.0
dy = 0.0
```

첫 번째 조건은 다음과 같아.

```python
p.x < 1.5 and dx < 0
```

두 조건 모두 참이므로 전체 결과는 참이야.

따라서 나머지 조건이 거짓이어도 `toward_wall`은 참이 돼.

```python
toward_wall = True
```

반대로 거북이가 화면 중앙에서 오른쪽을 향하고 있다면 다음과 같을 수 있어.

```python
p.x = 5.0
p.y = 5.0

dx = 1.0
dy = 0.0
```

어느 벽에도 가까이 있지 않으므로 네 조건이 모두 거짓이야.

```python
toward_wall = False
```

---

# 13. 속도 명령 만들기

벽을 향하고 있는지 판단했다면 이제 이동 명령을 만들 차례야.

```python
msg = Twist()

if toward_wall:
    msg.angular.z = 1.5
else:
    msg.linear.x = 1.0

self.publisher.publish(msg)
```

먼저 메시지를 생성해.

```python
msg = Twist()
```

새로운 `Twist` 메시지를 만들면 속도 값은 기본적으로 0이야.

따라서 다음과 같은 상태가 돼.

```text
linear.x  = 0.0
linear.y  = 0.0
linear.z  = 0.0

angular.x = 0.0
angular.y = 0.0
angular.z = 0.0
```

이후 조건에 따라 일부 값만 변경해.

## 13-1. 벽을 향하고 있다면

```python
if toward_wall:
    msg.angular.z = 1.5
```

`toward_wall`이 참이면 각속도를 1.5로 설정해.

```python
msg.angular.z = 1.5
```

직선 속도는 따로 설정하지 않았으므로 0이야.

결과적으로 다음과 같아.

```text
linear.x = 0.0
angular.z = 1.5
```

즉, 제자리에서 회전하도록 명령하는 거야.

turtlesim에서는 양의 각속도로 회전하면 일반적으로 반시계 방향으로 돌아.

다만 이 코드는 회전해야 할 각도를 계산하는 것은 아니야.

단지 회전 속도만 지정하고 있어.

## 13-2. 벽을 향하고 있지 않다면

```python
else:
    msg.linear.x = 1.0
```

벽을 향하고 있지 않으면 직선 속도를 1.0으로 설정해.

```text
linear.x = 1.0
angular.z = 0.0
```

따라서 거북이는 앞으로 이동해.

여기서도 회전 속도를 명시적으로 0으로 지정하지 않았지만, 새로운 `Twist()` 메시지의 기본값이 0이므로 회전하지 않는 명령이 돼.

## 13-3. 명령 발행

```python
self.publisher.publish(msg)
```

마지막으로 완성된 속도 명령을 발행해.

전체 동작을 표로 정리하면 다음과 같아.

| 상황 | `toward_wall` | `linear.x` | `angular.z` |
|---|---|---:|---:|
| 벽을 향함 | `True` | 0.0 | 1.5 |
| 벽을 향하지 않음 | `False` | 1.0 | 0.0 |

즉, 이 프로그램은 벽을 향하고 있으면 회전하고, 그렇지 않으면 직진하는 단순한 제어 규칙을 사용해.

---

# 14. 실제 상황을 숫자로 계산해 보기

이번에는 코드가 실제로 어떻게 판단하는지 네 가지 예시를 살펴보자.

## 예시 1: 화면 중앙에서 오른쪽으로 이동

위치와 방향이 다음과 같다고 가정해 보자.

```python
p.x = 5.0
p.y = 5.0
p.theta = 0.0
```

방향 성분을 계산하면 다음과 같아.

```python
dx = math.cos(0.0)  # 1.0
dy = math.sin(0.0)  # 0.0
```

네 가지 조건을 확인해 보자.

| 조건 | 결과 | 이유 |
|---|---|---|
| `p.x < 1.5 and dx < 0` | 거짓 | x 좌표가 충분히 큼 |
| `p.x > 9.5 and dx > 0` | 거짓 | 오른쪽 경계와 멂 |
| `p.y < 1.5 and dy < 0` | 거짓 | 아래쪽 경계와 멂 |
| `p.y > 9.5 and dy > 0` | 거짓 | 위쪽 경계와 멂 |

따라서 다음과 같아.

```python
toward_wall = False
```

최종 명령은 다음과 같아.

```python
msg.linear.x = 1.0
msg.angular.z = 0.0
```

거북이는 직진해.

## 예시 2: 왼쪽 벽에 가까이 있고 왼쪽을 향함

다음과 같다고 가정해 보자.

```python
p.x = 1.0
p.y = 5.0
p.theta = math.pi
```

`math.pi`는 약 3.14159이며 180도에 해당해.

방향 성분은 다음과 같아.

```python
dx = math.cos(math.pi)  # -1.0에 가까움
dy = math.sin(math.pi)  # 0.0에 가까움
```

따라서 다음 조건이 참이야.

```python
p.x < 1.5 and dx < 0
```

결과는 다음과 같아.

```python
toward_wall = True
```

따라서 회전 명령을 발행해.

```python
msg.linear.x = 0.0
msg.angular.z = 1.5
```

거북이는 제자리에서 회전하기 시작해.

## 예시 3: 왼쪽 벽에 가깝지만 오른쪽을 향함

이번에는 다음과 같다고 가정해 보자.

```python
p.x = 1.0
p.y = 5.0
p.theta = 0.0
```

방향 성분은 다음과 같아.

```python
dx = 1.0
dy = 0.0
```

첫 번째 조건을 확인하면 다음과 같아.

```python
p.x < 1.5 and dx < 0
```

좌표 조건은 참이지만 방향 조건은 거짓이야.

```text
True and False = False
```

나머지 벽 조건도 거짓이므로 최종 결과는 다음과 같아.

```python
toward_wall = False
```

따라서 거북이는 오른쪽으로 직진해.

즉, **벽 근처에 있다는 사실만으로 회전하지 않고, 벽을 향하고 있는지도 확인하는 거야.**

## 예시 4: 위쪽 벽에 가까이 있고 위쪽을 향함

다음과 같다고 가정해 보자.

```python
p.x = 5.0
p.y = 10.0
p.theta = math.pi / 2
```

방향 성분은 다음과 같아.

```python
dx = math.cos(math.pi / 2)  # 약 0
dy = math.sin(math.pi / 2)  # 1.0
```

위쪽 벽을 확인하는 조건은 다음과 같아.

```python
p.y > 9.5 and dy > 0
```

두 조건이 모두 참이므로 다음과 같아.

```python
toward_wall = True
```

따라서 거북이는 회전 명령을 받게 돼.

---

# 15. 이 프로그램이 완벽한 벽 회피 알고리즘은 아닌 이유

여기서 중요한 한계도 알아야 해.

현재 프로그램은 벽에 접근하는 상황을 감지해서 회전하지만, 실제로는 몇 가지 문제가 발생할 수 있어.

### 문제 1. 회전 방향을 상황에 맞게 결정하지 않음

현재 코드는 벽을 향하고 있으면 항상 다음 명령을 사용해.

```python
msg.angular.z = 1.5
```

따라서 왼쪽 벽에 접근하든 오른쪽 벽에 접근하든 같은 방향으로 회전해.

경우에 따라서는 벽에서 멀어지는 방향으로 돌아설 수 있지만, 항상 가장 적절한 방향으로 회전하는 것은 아니야.

### 문제 2. 회전이 끝나는 시점을 계산하지 않음

현재 코드는 벽을 향하고 있으면 계속 회전하도록 명령해.

```python
if toward_wall:
    msg.angular.z = 1.5
```

회전하면서 `theta`가 바뀌면 벽을 향하는지 여부도 달라져.

다음 타이머 실행 때 `toward_wall`이 거짓이 되면 직진 명령으로 바뀌어.

따라서 실제로는 위치와 방향이 변하면서 회전과 직진이 반복될 수 있어.

### 문제 3. 대각선 방향에서는 조건이 단순함

예를 들어 거북이가 오른쪽 위 대각선 방향을 향하고 있다고 가정해 보자.

```python
dx = 0.707
dy = 0.707
```

거북이가 오른쪽 벽과 위쪽 벽 모두에 가까워지면 두 조건이 동시에 참이 될 수 있어.

하지만 현재 프로그램은 두 벽 중 어느 쪽을 피하는 것이 더 좋은지 계산하지 않아.

### 문제 4. 위치 정보만 사용함

현재 코드에서는 `Pose` 메시지의 좌표와 방향을 사용해.

```python
p.x
p.y
p.theta
```

실제 로봇에서 벽을 피하려면 일반적으로 LiDAR, 초음파 센서, 깊이 카메라 등으로 장애물까지의 거리를 측정해야 해.

따라서 이 프로그램은 **벽의 위치를 직접 감지하는 것이 아니라, 거북이의 위치와 방향으로 벽에 접근할 상황을 추정하는 실습**이라고 이해하면 정확해.

---

# 16. `main()` 함수 이해하기

마지막으로 프로그램 실행 부분을 살펴보자.

```python
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
```

이 부분은 이전 실습과 동일한 구조야.

### ① ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 프로그램을 초기화해.

### ② 노드 생성

```python
node = TurtleCmdAndPose()
```

노드 객체를 만들면서 Publisher, Subscriber, Timer를 생성해.

### ③ 노드 실행

```python
rclpy.spin(node)
```

노드가 실행되는 동안 Subscriber의 콜백과 Timer의 콜백을 처리해.

이번 코드에서는 두 함수가 중요해.

```python
self.on_pose
```

위치 메시지가 도착했을 때 실행되는 콜백이야.

```python
self.publish_velocity
```

타이머가 만료되었을 때 실행되는 콜백이야.

### ④ 종료 처리

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

터미널에서 `Ctrl + C`를 눌러 종료할 때 노드와 ROS 2 실행 상태를 정리해.

---

# 17. Ubuntu에서 직접 실행하기

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 환경에서 실행해 보자.

## 터미널 1: turtlesim 실행

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

거북이 시뮬레이터 창이 열릴 거야.

## 터미널 2: 워크스페이스 빌드

코드가 `turtle_robot` 패키지에 들어 있다고 가정하면 다음과 같이 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 다음 명령어를 실행해.

```bash
source install/setup.bash
```

## 터미널 2: 프로그램 실행

`setup.py`의 실행 이름이 `lesson_06_turtle_cmd_and_pose`라면 다음과 같이 실행해.

```bash
ros2 run turtle_robot lesson_06_turtle_cmd_and_pose
```

실행 이름이 다르다면 `setup.py`에 등록된 이름을 사용해야 해.

## 터미널 3: 위치 확인

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /turtle1/pose
```

거북이의 위치와 방향이 계속 출력될 거야.

예를 들어 다음과 같은 데이터가 나타날 수 있어.

```yaml
x: 5.0
y: 5.0
theta: 0.0
linear_velocity: 1.0
angular_velocity: 0.0
```

거북이가 이동하거나 회전하면 `x`, `y`, `theta` 값이 바뀌는 것을 확인할 수 있어.

단, `ros2 topic echo`를 실행하는 동안에는 출력이 계속 이어지므로 종료하려면 `Ctrl + C`를 누르면 돼.

---

# 18. 이번 실습에서 꼭 기억해야 할 핵심

이번 코드의 핵심은 위치 정보를 사용해 이동 명령을 결정한다는 것이야.

전체 흐름을 다시 정리해 보자.

| 순서 | 코드 | 역할 |
|---|---|---|
| 1 | `create_publisher()` | 속도 명령 발행 준비 |
| 2 | `create_subscription()` | 위치 정보 수신 준비 |
| 3 | `on_pose()` | 수신한 위치 저장 |
| 4 | `math.cos(p.theta)` | x축 방향 성분 계산 |
| 5 | `math.sin(p.theta)` | y축 방향 성분 계산 |
| 6 | `toward_wall` | 벽을 향하는지 판단 |
| 7 | `msg.angular.z = 1.5` | 회전 명령 설정 |
| 8 | `msg.linear.x = 1.0` | 직진 명령 설정 |
| 9 | `publish(msg)` | 속도 명령 발행 |

마지막으로 아래 세 가지를 반드시 이해하고 넘어가면 좋아.

**첫째, `self.pose = message`**

Subscriber가 수신한 위치 정보를 저장하는 코드야.

**둘째, `dx = math.cos(p.theta)`와 `dy = math.sin(p.theta)`**

거북이가 바라보는 방향을 x축과 y축 성분으로 바꾸는 코드야.

**셋째, `toward_wall`**

거북이의 위치와 이동 방향을 함께 확인해서 벽을 향하고 있는지 판단하는 조건이야.

이 세 가지를 이해하면 단순히 명령을 보내는 Publisher를 넘어, **현재 상태를 확인하고 그 결과에 따라 로봇의 동작을 바꾸는 기본적인 제어 구조**를 이해한 거야.

