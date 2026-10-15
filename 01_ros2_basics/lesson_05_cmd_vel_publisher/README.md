
# 1. 전체 코드 이해하기

먼저 프로그램의 동작을 간단하게 살펴보자.

```text
┌──────────────────────────────┐
│ CmdVelPublisher 노드 실행     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Publisher 생성               │
│ /turtle1/cmd_vel             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Timer 생성                   │
│ 0.1초마다 실행               │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ publish_velocity() 실행      │
│                              │
│ 1. Twist 메시지 생성         │
│ 2. 속도 증가                 │
│ 3. 직선 속도 설정            │
│ 4. 회전 속도 설정            │
│ 5. 메시지 발행                │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ turtlesim이 속도 명령 수신   │
│ 거북이 이동                  │
└──────────────────────────────┘
```

핵심은 **Publisher가 속도 명령을 발행하고, turtlesim이 그 명령을 받아 거북이를 움직인다는 것**이야.

---

# 2. 코드 한 줄씩 이해하기

## ① Twist 메시지 가져오기

```python
from geometry_msgs.msg import Twist  # noqa: F401
```

### Twist란?

`Twist`는 로봇의 선속도와 각속도를 표현하는 ROS 2 메시지 타입이야.

쉽게 말하면 로봇에게 다음과 같은 명령을 전달하는 데 사용해.

- 앞으로 이동해.
- 옆으로 이동해.
- 위아래로 이동해.
- 회전해.

`Twist` 메시지에는 크게 두 가지 정보가 있어.

| 속성 | 의미 | 주요 사용 예시 |
|---|---|---|
| `linear` | 직선 방향의 속도 | 앞으로 이동 |
| `angular` | 회전 방향의 각속도 | 제자리 회전 |

각 속성에는 x, y, z 세 가지 값이 있어.

```python
msg.linear.x = 1.0
msg.linear.y = 0.0
msg.linear.z = 0.0

msg.angular.x = 0.0
msg.angular.y = 0.0
msg.angular.z = 0.0
```

각 값의 의미는 다음과 같아.

| 속성 | 의미 |
|---|---|
| `linear.x` | x축 방향 직선 속도 |
| `linear.y` | y축 방향 직선 속도 |
| `linear.z` | z축 방향 직선 속도 |
| `angular.x` | x축 기준 회전 속도 |
| `angular.y` | y축 기준 회전 속도 |
| `angular.z` | z축 기준 회전 속도 |

일반적인 2D turtlesim에서는 주로 다음 두 가지를 사용해.

```python
msg.linear.x = 1.0
msg.angular.z = 0.0
```

이렇게 설정하면 거북이는 앞으로 이동하면서 회전하지 않아.

반대로 다음과 같이 설정하면 어떻게 될까?

```python
msg.linear.x = 1.0
msg.angular.z = 2.0
```

앞으로 이동하면서 동시에 회전하기 때문에 곡선 궤적을 그리게 돼.

참고로 `Twist`의 속도 값은 일반적으로 선속도는 m/s, 각속도는 rad/s 단위를 사용해. turtlesim에서는 화면상의 좌표와 이동 속도를 다루므로 실제 로봇의 물리적 이동 거리와는 구분해야 해.

### `# noqa: F401`은 무엇일까?

```python
from geometry_msgs.msg import Twist  # noqa: F401
```

`F401`은 일반적으로 가져온 모듈이나 변수를 사용하지 않았을 때 발생하는 정적 분석 경고 코드야.

`# noqa: F401`은 해당 줄의 사용하지 않은 가져오기 경고를 무시하라는 뜻이야.

현재 코드에서는 `Twist`를 실제로 사용하고 있으므로 이 주석이 반드시 필요한 것은 아니야.

---

## ② ROS 2 라이브러리 가져오기

```python
import rclpy
from rclpy.node import Node
```

두 줄은 ROS 2 Python 프로그램을 작성하기 위한 기본 코드야.

### `rclpy`

```python
import rclpy
```

`rclpy`는 ROS 2에서 Python을 사용할 수 있도록 해주는 라이브러리야.

대표적으로 다음 기능을 제공해.

- ROS 2 초기화
- 노드 실행
- 통신 처리
- 프로그램 종료

### `Node`

```python
from rclpy.node import Node
```

`Node`는 ROS 2 노드를 만들기 위한 기본 클래스야.

노드는 로봇 시스템에서 하나의 기능을 담당하는 프로그램 단위라고 이해하면 돼.

예를 들어 다음과 같은 노드를 만들 수 있어.

| 노드 | 역할 |
|---|---|
| `CmdVelPublisher` | 속도 명령 발행 |
| `PoseSubscriber` | 거북이 위치 수신 |
| `SpawnClient` | 새로운 거북이 생성 요청 |
| `CameraNode` | 카메라 데이터 처리 |

이번 실습에서는 거북이에게 속도를 전달하는 노드를 만드는 거야.

---

# 3. CmdVelPublisher 클래스

```python
class CmdVelPublisher(Node):
    """거북이 속도를 발행하는 노드입니다."""
```

여기서 중요한 개념은 `class`와 `Node`의 상속이야.

### 클래스란?

클래스는 객체를 만들기 위한 설계도라고 생각하면 돼.

예를 들어 다음 코드를 보자.

```python
class Robot:
    pass
```

`Robot`이라는 클래스를 정의한 거야.

그런데 이번 코드에서는 다음과 같이 작성했어.

```python
class CmdVelPublisher(Node):
```

괄호 안에 `Node`가 들어 있지?

이것은 `CmdVelPublisher`가 ROS 2의 `Node` 클래스를 상속받는다는 뜻이야.

따라서 `CmdVelPublisher`는 ROS 2 노드가 제공하는 여러 기능을 사용할 수 있어.

예를 들어 다음과 같은 기능이 있어.

```python
self.create_publisher()
self.create_timer()
```

이 두 기능을 이용해 메시지를 발행하고 일정 시간마다 함수를 실행할 수 있어.

**기억할 점:** ROS 2에서는 일반적인 Python 클래스를 만드는 것뿐만 아니라 `Node`를 상속받아 ROS 2 노드로 구성하는 방법을 자주 사용해.

---

# 4. `__init__()` 함수

```python
def __init__(self):
    super().__init__('lesson_05_cmd_vel_publisher')
```

`__init__()`은 객체를 생성할 때 실행되는 초기화 함수야.

다음 코드를 실행한다고 생각해 보자.

```python
node = CmdVelPublisher()
```

그러면 Python은 `CmdVelPublisher` 객체를 만들면서 `__init__()`을 실행해.

### `self`란?

```python
def __init__(self):
```

`self`는 현재 객체 자신을 가리켜.

예를 들어 다음 코드를 보자.

```python
self.linear_speed = 0.2
```

이것은 현재 `CmdVelPublisher` 객체가 `linear_speed`라는 값을 보관하도록 하는 거야.

나중에 다른 메서드에서도 다음과 같이 접근할 수 있어.

```python
self.linear_speed += 0.01
```

### `super().__init__()`은 무엇일까?

```python
super().__init__('lesson_05_cmd_vel_publisher')
```

부모 클래스인 `Node`의 초기화 기능을 실행하는 코드야.

괄호 안의 문자열은 ROS 2에서 사용할 노드 이름이야.

따라서 노드 이름은 다음과 같아.

```text
lesson_05_cmd_vel_publisher
```

터미널에서 다음 명령어로 실행 중인 노드를 확인할 수 있어.

```bash
ros2 node list
```

실행 중이라면 다음과 비슷한 결과가 나와.

```text
/lesson_05_cmd_vel_publisher
/turtlesim
```

`/turtlesim`은 거북이 시뮬레이터 노드야.

---

# 5. Publisher 생성하기

```python
self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
```

이번 실습에서 가장 중요한 코드 중 하나야.

이 한 줄을 세 부분으로 나눠 보자.

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

### 첫 번째: `Twist`

```python
Twist
```

발행할 메시지의 종류를 지정해.

이번에는 속도 정보를 전달해야 하므로 `Twist`를 사용하는 거야.

예를 들어 위치를 나타내는 메시지나 카메라 이미지 메시지를 발행한다면 다른 메시지 타입을 사용할 수 있어.

### 두 번째: `/turtle1/cmd_vel`

```python
'/turtle1/cmd_vel'
```

이것은 **토픽(Topic)의 이름**이야.

토픽은 ROS 2 노드 사이에서 메시지를 주고받는 통신 경로라고 생각하면 돼.

이번 프로그램에서는 다음과 같이 통신해.

```text
CmdVelPublisher
       │
       │ Twist 메시지 발행
       ▼
/turtle1/cmd_vel
       │
       │ 속도 명령 전달
       ▼
    turtlesim
       │
       ▼
  거북이 이동
```

여기서 `/turtle1/cmd_vel`은 첫 번째 거북이의 속도 명령을 전달하는 토픽이야.

### 세 번째: `10`

```python
10
```

이 값은 Publisher가 사용하는 QoS 설정 중 메시지 보관 깊이(depth)를 지정하는 값이야.

이 코드에서는 정수 `10`을 전달하므로 일반적으로 기본적인 QoS 설정과 함께 큐 깊이 10을 사용하는 형태가 돼.

쉽게 설명하면 메시지가 바로 처리되지 못하는 상황에 대비해 큐에 보관할 메시지 수를 설정하는 거야.

### `self.publisher`는 무엇일까?

```python
self.publisher = self.create_publisher(...)
```

생성된 Publisher 객체를 `self.publisher`에 저장해.

이후 다른 메서드에서 다음과 같이 사용할 수 있어.

```python
self.publisher.publish(msg)
```

즉, Publisher를 생성하는 것과 메시지를 발행하는 것은 서로 다른 작업이야.

- `create_publisher()`: 메시지를 발행할 준비를 한다.
- `publish()`: 실제 메시지를 발행한다.

---

# 6. Timer 생성하기

```python
self.timer = self.create_timer(0.1, self.publish_velocity)
```

이 코드는 일정한 간격으로 함수를 실행하도록 타이머를 생성하는 코드야.

여기서는 두 가지를 지정하고 있어.

```python
self.create_timer(0.1, self.publish_velocity)
```

| 인자 | 의미 |
|---|---|
| `0.1` | 타이머 간격, 초 단위 |
| `self.publish_velocity` | 실행할 함수 |

따라서 `publish_velocity()`를 약 0.1초마다 실행하도록 설정한 거야.

### 0.1초는 몇 초당 한 번일까?

계산하면 다음과 같아.

```text
1초 ÷ 0.1초 = 10회
```

즉, 이론적으로 초당 10번 실행하는 설정이야.

실제 실행 횟수는 컴퓨터 성능과 ROS 2 실행 상태 등에 따라 달라질 수 있어.

### 왜 타이머를 사용할까?

만약 타이머 없이 다음과 같이 작성하면 어떨까?

```python
msg = Twist()
msg.linear.x = 1.0
self.publisher.publish(msg)
```

이 코드는 해당 위치에서 한 번 실행될 뿐이야.

반면 타이머를 사용하면 주기적으로 속도 명령을 보낼 수 있어.

```text
0.1초 → 속도 명령 발행
0.2초 → 속도 명령 발행
0.3초 → 속도 명령 발행
0.4초 → 속도 명령 발행
0.5초 → 속도 명령 발행
...
```

이렇게 반복해서 명령을 보내는 방식은 로봇 제어에서 자주 사용돼.

---

# 7. `linear_speed` 변수

```python
self.linear_speed = 0.2
```

이 코드는 직선 속도를 저장할 변수를 만들고 초기값을 `0.2`로 설정하는 코드야.

여기서 중요한 점은 `self.linear_speed`가 클래스의 인스턴스 변수라는 거야.

즉, 객체가 유지되는 동안 값을 저장하고 사용할 수 있어.

현재 코드에서는 처음에 다음과 같은 값을 갖게 돼.

```python
self.linear_speed = 0.2
```

그런데 `publish_velocity()` 함수 안에서는 다음과 같이 작성했어.

```python
self.linear_speed += 0.01
```

이 부분이 실제 동작을 결정하는 중요한 요소야.

### `+=` 연산자 이해하기

다음 두 코드는 같은 의미야.

```python
self.linear_speed += 0.01
```

```python
self.linear_speed = self.linear_speed + 0.01
```

현재 값에 `0.01`을 더하고 그 결과를 다시 저장하는 거야.

실제 값을 살펴보자.

| 실행 횟수 | 실행 전 속도 | 증가량 | 실행 후 속도 |
|---:|---:|---:|---:|
| 초기 상태 | - | - | 0.20 |
| 1회 | 0.20 | +0.01 | 0.21 |
| 2회 | 0.21 | +0.01 | 0.22 |
| 3회 | 0.22 | +0.01 | 0.23 |
| 4회 | 0.23 | +0.01 | 0.24 |
| 5회 | 0.24 | +0.01 | 0.25 |

타이머가 약 0.1초마다 실행되므로 속도도 그때마다 증가해.

따라서 약 1초가 지나면 속도는 초기값보다 약 `0.1` 증가해.

**주의:** 현재 코드에는 속도 증가에 상한이 없어. 프로그램을 오랫동안 실행하면 속도가 계속 증가한다는 점을 기억해야 해.

---

# 8. `publish_velocity()` 함수

이제 실제로 메시지를 만들어 발행하는 부분을 살펴보자.

```python
def publish_velocity(self):
    """거북이의 속도를 발행합니다."""

    msg = Twist()
    self.linear_speed += 0.01
    msg.linear.x = self.linear_speed
    msg.angular.z = 2.0
    self.publisher.publish(msg)
```

한 줄씩 설명할게.

## ① Twist 메시지 생성

```python
msg = Twist()
```

`Twist` 메시지 객체를 생성하는 코드야.

메시지에 속도 값을 지정하기 전에는 일반적으로 각 필드가 기본값인 `0.0`으로 초기화돼.

예를 들어 다음과 같아.

```python
msg.linear.x
msg.linear.y
msg.linear.z

msg.angular.x
msg.angular.y
msg.angular.z
```

모두 기본값이 `0.0`이야.

이제 필요한 속도 값을 지정할 수 있어.

## ② 속도 증가

```python
self.linear_speed += 0.01
```

앞에서 설명했듯이 저장된 속도 값에 `0.01`을 더해.

처음 실행할 때는 다음과 같이 계산돼.

```text
초기값: 0.20
증가량: 0.01
결과:   0.21
```

다음 실행에서는 `0.21`에 `0.01`을 더해 `0.22`가 돼.

## ③ 직선 속도 지정

```python
msg.linear.x = self.linear_speed
```

메시지의 x축 직선 속도에 현재 `linear_speed` 값을 넣는 코드야.

첫 번째 실행에서는 다음과 같아.

```python
msg.linear.x = 0.21
```

두 번째 실행에서는 다음과 같아.

```python
msg.linear.x = 0.22
```

이렇게 실행할 때마다 값이 달라져.

turtlesim에서 `linear.x`는 거북이의 앞뒤 이동 속도를 결정해.

양수라면 거북이의 현재 앞쪽 방향으로 이동하고, 음수라면 뒤쪽으로 이동해.

여기서는 양수를 사용하므로 앞으로 이동하게 돼.

## ④ 각속도 지정

```python
msg.angular.z = 2.0
```

이 코드는 거북이의 z축 기준 각속도를 `2.0`으로 지정해.

2D turtlesim에서는 이 값이 거북이의 회전 속도를 결정해.

일반적으로 다음과 같이 이해하면 돼.

| `angular.z` 값 | 의미 |
|---:|---|
| `0.0` | 회전하지 않음 |
| `1.0` | 한 방향으로 회전 |
| `2.0` | 같은 방향으로 더 빠르게 회전 |
| `-1.0` | 반대 방향으로 회전 |

양수와 음수 중 어느 방향이 화면에서 시계 방향인지는 좌표계와 표시 방향을 함께 고려해야 해. turtlesim에서는 일반적으로 양수일 때 반시계 방향으로 회전해.

### 현재 코드의 결과

현재 설정을 정리하면 다음과 같아.

```python
msg.linear.x = self.linear_speed
msg.angular.z = 2.0
```

즉,

- 앞으로 이동한다.
- 동시에 회전한다.
- 앞으로 이동하는 속도는 점점 증가한다.

따라서 거북이는 일정한 속도로 직진하지 않고 점점 빨라지면서 회전하는 궤적을 그리게 돼.

---

# 9. Publisher로 메시지 발행하기

```python
self.publisher.publish(msg)
```

이 코드가 실제 메시지를 발행하는 부분이야.

지금까지 만든 `msg` 객체를 `/turtle1/cmd_vel` 토픽으로 발행하는 거지.

예를 들어 메시지의 값이 다음과 같다고 해 보자.

```python
msg.linear.x = 0.21
msg.angular.z = 2.0
```

그러면 이 속도 명령을 Publisher가 발행해.

ROS 2에서는 이 메시지를 구독하고 있는 노드가 받을 수 있어.

이번 실습에서는 turtlesim이 `/turtle1/cmd_vel`을 구독하고 있어.

다음 명령어로 확인할 수 있어.

```bash
ros2 topic info /turtle1/cmd_vel
```

메시지 타입을 확인하려면 다음 명령어를 사용해.

```bash
ros2 topic type /turtle1/cmd_vel
```

예상 결과는 다음과 같아.

```text
geometry_msgs/msg/Twist
```

실제로 발행되는 메시지를 관찰하고 싶다면 다음 명령어를 실행해 봐.

```bash
ros2 topic echo /turtle1/cmd_vel
```

그러면 다음과 비슷한 메시지를 볼 수 있어.

```yaml
linear:
  x: 0.21
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 2.0
```

다음 메시지에서는 `linear.x`가 `0.22`, 그다음에는 `0.23`으로 증가하는 것을 관찰할 수 있어.

---

# 10. `main()` 함수

이제 노드를 실행하는 부분을 살펴보자.

```python
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
```

## ① ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 프로그램을 실행하기 위한 초기화 코드야.

일반적으로 노드를 생성하기 전에 실행해야 해.

## ② 노드 객체 생성

```python
node = CmdVelPublisher()
```

앞에서 정의한 `CmdVelPublisher` 클래스로 객체를 만들어.

이 과정에서 `__init__()`이 실행되면서 다음 작업이 수행돼.

1. 노드 이름 설정
2. Publisher 생성
3. Timer 생성
4. 초기 속도 설정

## ③ 노드 실행

```python
rclpy.spin(node)
```

이 코드는 노드가 계속 실행되면서 콜백을 처리하도록 해.

이번 실습에서는 타이머가 핵심이야.

```python
self.timer = self.create_timer(0.1, self.publish_velocity)
```

`rclpy.spin(node)`가 실행 중인 동안 타이머가 만료되면 `publish_velocity()`가 호출돼.

쉽게 말해 노드를 계속 실행하면서 주기적으로 속도 명령을 발행하도록 하는 거야.

## ④ 키보드로 종료할 때

```python
except KeyboardInterrupt:
    pass
```

터미널에서 `Ctrl + C`를 눌러 프로그램을 종료하면 일반적으로 `KeyboardInterrupt`가 발생해.

여기서는 해당 예외를 받아 별도의 처리를 하지 않도록 했어.

## ⑤ 노드 정리 및 ROS 2 종료

```python
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

프로그램이 종료될 때 실행되는 정리 코드야.

```python
node.destroy_node()
```

노드가 사용하던 리소스를 정리해.

```python
rclpy.try_shutdown()
```

ROS 2의 실행 상태를 종료해. 이미 종료된 경우에도 안전하게 종료 처리를 시도할 수 있어.

---

# 11. 마지막 실행 조건

```python
if __name__ == '__main__':
    main()
```

이 코드는 Python 프로그램을 직접 실행했을 때 `main()` 함수를 호출하도록 해.

예를 들어 파일 이름이 다음과 같다고 하자.

```text
lesson_05_cmd_vel_publisher.py
```

터미널에서 해당 파일을 직접 실행하면 `main()`이 호출돼.

반대로 다른 Python 파일에서 이 파일을 모듈로 가져오는 경우에는 일반적으로 `main()`이 자동으로 실행되지 않아.

이 패턴은 ROS 2 Python 패키지에서 자주 볼 수 있어.

---

# 12. 실습 설명대로 직진하도록 수정하기

여기까지 이해했다면 실제 실습의 요구사항을 다시 확인해 보자.

코드의 주석에는 다음과 같이 적혀 있어.

```python
# 실습 3: Twist 메시지를 만들고 linear.x를 1.0으로 설정하여 발행하세요.
```

그런데 현재 코드는 다음과 같아.

```python
msg = Twist()
self.linear_speed += 0.01
msg.linear.x = self.linear_speed
msg.angular.z = 2.0
```

실습 설명과 실제 코드가 다른 거야.

**실습 목표가 일정한 속도로 직진하는 것이라면 다음과 같이 수정하면 돼.**

```python
def publish_velocity(self):
    """거북이의 속도를 발행합니다."""
    msg = Twist()
    msg.linear.x = 1.0
    msg.angular.z = 0.0
    self.publisher.publish(msg)
```

수정된 코드는 다음과 같이 동작해.

| 속성 | 설정값 | 결과 |
|---|---:|---|
| `linear.x` | `1.0` | 앞으로 이동 |
| `linear.y` | `0.0` | 옆으로 이동하지 않음 |
| `linear.z` | `0.0` | 위아래로 이동하지 않음 |
| `angular.x` | `0.0` | x축 기준 회전 없음 |
| `angular.y` | `0.0` | y축 기준 회전 없음 |
| `angular.z` | `0.0` | 2D 평면에서 회전하지 않음 |

여기서는 `Twist()`의 기본값이 `0.0`이므로 `linear.y`, `linear.z`, `angular.x`, `angular.y`를 따로 설정하지 않아도 돼.

전체 코드를 수정하면 다음과 같아.

```python
"""거북이를 직진시키는 Publisher 실습입니다."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node


class CmdVelPublisher(Node):
    """거북이 속도를 발행하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_05_cmd_vel_publisher')

        # Publisher 생성
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 0.1초마다 속도 명령 발행
        self.timer = self.create_timer(
            0.1,
            self.publish_velocity
        )

    def publish_velocity(self):
        """거북이의 속도를 발행합니다."""
        msg = Twist()

        # 앞으로 이동
        msg.linear.x = 1.0

        # 회전하지 않음
        msg.angular.z = 0.0

        # 속도 명령 발행
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
```

이렇게 수정하면 실습 설명에 맞게 일정한 속도로 직진하는 명령을 발행할 수 있어.

단, turtlesim의 화면 경계에 도달하면 거북이가 화면 밖으로 나갈 수 없으므로 계속 직진하지는 못해.

---

# 13. Ubuntu에서 직접 실행해 보기

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 학습 환경에서 다음 순서로 확인하면 돼.

### 터미널 1: turtlesim 실행

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

거북이 시뮬레이터 창이 열릴 거야.

### 터미널 2: 학습 워크스페이스 설정

워크스페이스가 `~/ros2_ws`라면 다음 명령어를 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
```

패키지를 수정했다면 빌드해.

```bash
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 워크스페이스를 적용해.

```bash
source install/setup.bash
```

여기서 `turtle_robot`은 현재 코드가 해당 패키지에 들어 있는 경우를 가정한 이름이야. 실제 패키지 이름이 다르다면 그 이름으로 바꿔야 해.

### 터미널 2: 노드 실행

패키지의 `setup.py`에 등록한 실행 이름이 `lesson_05_cmd_vel_publisher`라면 다음 명령어로 실행할 수 있어.

```bash
ros2 run turtle_robot lesson_05_cmd_vel_publisher
```

실행 이름이 다르면 `setup.py`의 `console_scripts`에 등록된 이름을 사용해야 해.

### 터미널 3: 토픽 확인

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /turtle1/cmd_vel
```

메시지가 계속 출력되면 Publisher가 정상적으로 속도 명령을 발행하고 있는 거야.

실행을 멈추려면 Publisher가 실행 중인 터미널에서 `Ctrl + C`를 눌러.

---

# 14. 이번 실습에서 꼭 기억할 핵심 5가지

| 개념 | 코드 | 역할 |
|---|---|---|
| 노드 생성 | `class CmdVelPublisher(Node)` | ROS 2 노드 정의 |
| Publisher 생성 | `create_publisher()` | 메시지를 발행할 준비 |
| 토픽 지정 | `'/turtle1/cmd_vel'` | 메시지 통신 경로 지정 |
| Timer 생성 | `create_timer(0.1, ...)` | 약 0.1초마다 콜백 실행 |
| 메시지 발행 | `self.publisher.publish(msg)` | 실제 속도 명령 전달 |

그리고 가장 중요한 부분은 다음 두 줄이야.

```python
msg.linear.x = 1.0
msg.angular.z = 0.0
```

첫 번째는 앞으로 이동하라는 뜻이고, 두 번째는 회전하지 말라는 뜻이야.

