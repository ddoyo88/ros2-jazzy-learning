
# 1. 이번 실습에서 배우는 핵심

이번 실습의 목표는 거북이의 위치를 계속 확인해서 터미널에 출력하는 거야.

예를 들어 거북이가 움직이면 다음과 같은 메시지가 출력돼.

```text
[INFO] [lesson_01_pose_subscriber]: x=5.54, y=5.54, theta=0.00
[INFO] [lesson_01_pose_subscriber]: x=5.64, y=5.54, theta=0.00
[INFO] [lesson_01_pose_subscriber]: x=5.74, y=5.54, theta=0.00
```

거북이가 이동하면 `x`, `y` 값이 바뀌고, 회전하면 `theta` 값이 바뀌어.

이것을 가능하게 하는 것이 **토픽(Topic)과 구독자(Subscriber)** 야.

## 1-1. ROS 2의 통신 구조

먼저 다음 그림을 이해하자.

```text
┌──────────────────────────┐
│   turtlesim_node         │
│                          │
│ 거북이의 현재 위치 계산   │
└────────────┬─────────────┘
             │
             │ Publish (발행)
             ▼
      /turtle1/pose
      메시지 타입: Pose
             │
             │ Subscribe (구독)
             ▼
┌──────────────────────────┐
│   PoseSubscriber         │
│                          │
│ x, y, theta 출력          │
└──────────────────────────┘
```

각 구성 요소의 역할은 다음과 같아.

| 구성 요소 | 역할 |
|---|---|
| `turtlesim_node` | 거북이 시뮬레이터를 실행하고 위치를 계산 |
| `/turtle1/pose` | 거북이의 위치 정보를 전달하는 토픽 |
| `Pose` | 전달되는 데이터의 구조를 정의하는 메시지 타입 |
| `PoseSubscriber` | 토픽을 구독하고 위치 정보를 출력하는 노드 |
| `on_pose()` | 메시지가 도착했을 때 실행되는 콜백 함수 |

여기서 가장 중요한 것은 **토픽은 데이터를 전달하는 통로이고, 메시지는 그 통로를 통해 전달되는 데이터의 형식**이라는 점이야.

---

# 2. 먼저 토픽과 메시지를 확인하자

실습 코드부터 작성하기 전에 ROS 2에서 실제로 어떤 데이터가 전달되는지 확인해 보자.

### ① turtlesim 실행

터미널 A에서 실행해.

```bash
ros2 run turtlesim turtlesim_node
```

그러면 거북이가 있는 시뮬레이터 창이 나타나.

터미널 B에서는 키보드로 거북이를 움직일 수 있도록 실행해.

```bash
ros2 run turtlesim turtle_teleop_key
```

이제 터미널 C를 열어서 다음 명령어를 입력해.

### ② 토픽의 메시지 타입 확인

```bash
ros2 topic type /turtle1/pose
```

예상 출력:

```text
turtlesim_msgs/msg/Pose
```

설치된 ROS 2 배포판의 메시지 패키지 이름에 따라 출력이 달라질 수 있는데, Jazzy의 기본 turtlesim에서는 일반적으로 다음과 같이 나와.

```text
turtlesim/msg/Pose
```

이 명령어의 의미는 다음과 같아.

- `ros2 topic`: 토픽 관련 명령어
- `type`: 해당 토픽이 사용하는 메시지 타입 확인
- `/turtle1/pose`: 확인할 토픽 이름

즉, **이 토픽에서 어떤 형태의 데이터를 받아야 하는지 확인하는 명령어**야.

### ③ 메시지의 구조 확인

```bash
ros2 interface show turtlesim/msg/Pose
```

출력 예시:

```text
float32 x
float32 y
float32 theta
float32 linear_velocity
float32 angular_velocity
```

각 필드는 다음과 같은 의미야.

| 필드 | 의미 | 예시 |
|---|---|---|
| `x` | 거북이의 가로 위치 | `5.54` |
| `y` | 거북이의 세로 위치 | `5.54` |
| `theta` | 거북이의 방향각 | `0.00` |
| `linear_velocity` | 직선 이동 속도 | `1.00` |
| `angular_velocity` | 회전 속도 | `0.00` |

여기서 `theta`는 라디안(radian) 단위야.

- `0` 라디안: 오른쪽 방향
- 약 `1.57` 라디안: 위쪽 방향
- 약 `3.14` 라디안: 왼쪽 방향
- 약 `-1.57` 라디안: 아래쪽 방향

이는 turtlesim 화면의 좌표계 기준이야.

### ④ 토픽에 실제로 전달되는 데이터 확인

```bash
ros2 topic echo /turtle1/pose
```

예상 출력:

```yaml
x: 5.544445
y: 5.544445
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

거북이를 움직이면 위치와 속도 값이 바뀌는 것을 볼 수 있어.

이 명령어는 우리가 작성할 `PoseSubscriber`와 비슷한 역할을 해. 다만 직접 만든 Python 노드 대신 ROS 2 CLI 도구를 이용해서 토픽을 확인하는 거야.

---

# 3. Python 코드 한 줄씩 이해하기

이제 실습 파일을 살펴보자.

파일 경로는 다음과 같아.

```text
~/ros2_ws/src/turtle_robot/turtle_robot/lesson_01_pose_subscriber.py
```

## 3-1. 필요한 라이브러리 가져오기

```python
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
```

각 줄의 역할을 알아보자.

### `import rclpy`

```python
import rclpy
```

`rclpy`는 Python에서 ROS 2 기능을 사용할 수 있게 해주는 라이브러리야.

ROS 2 노드를 초기화하고 실행하거나 종료할 때 사용해.

대표적인 함수는 다음과 같아.

| 함수 | 역할 |
|---|---|
| `rclpy.init()` | ROS 2 초기화 |
| `rclpy.spin()` | 노드의 콜백 처리 |
| `rclpy.shutdown()` | ROS 2 종료 |

### `from rclpy.node import Node`

```python
from rclpy.node import Node
```

ROS 2 노드를 만들기 위해 `Node` 클래스를 가져오는 거야.

우리가 만드는 `PoseSubscriber`는 이 `Node`를 상속받아.

### `from turtlesim.msg import Pose`

```python
from turtlesim.msg import Pose
```

거북이 위치를 전달하는 메시지 타입인 `Pose`를 가져와.

앞에서 확인한 다음 명령어와 연결되는 부분이야.

```bash
ros2 topic type /turtle1/pose
```

토픽이 `Pose` 타입의 메시지를 사용하므로 Python 코드에서도 같은 타입을 사용해야 해.

**핵심:** 토픽의 메시지 타입을 먼저 확인하고, 그 타입에 맞춰 구독자를 작성하는 거야.

---

## 3-2. Subscriber 노드 만들기

```python
class PoseSubscriber(Node):
```

이 코드는 `PoseSubscriber`라는 클래스를 정의해.

여기서 `Node`는 부모 클래스이고, `PoseSubscriber`는 자식 클래스야.

쉽게 말하면 ROS 2 노드가 갖춰야 할 기본 기능을 물려받아 우리가 원하는 기능을 추가하는 거야.

```text
Node
 │
 └── PoseSubscriber
       │
       ├── 토픽 구독
       └── 위치 출력
```

이렇게 클래스를 작성하면 구독 기능을 하나의 노드로 구성할 수 있어.

---

## 3-3. 노드 초기화하기

```python
def __init__(self):
    super().__init__('lesson_01_pose_subscriber')
```

`__init__()`은 객체를 생성할 때 실행되는 초기화 함수야.

예를 들어 다음 코드를 실행하면,

```python
node = PoseSubscriber()
```

`PoseSubscriber` 객체가 생성되면서 `__init__()`이 실행돼.

그 안의 다음 코드가 ROS 2 노드를 초기화해.

```python
super().__init__('lesson_01_pose_subscriber')
```

여기서 중요한 부분은 다음과 같아.

- `super().__init__()`: 부모 클래스인 `Node`의 초기화 기능을 호출
- `'lesson_01_pose_subscriber'`: 노드 이름

따라서 ROS 2에서 이 노드는 다음 이름으로 표시돼.

```text
/lesson_01_pose_subscriber
```

실제로 확인하려면 다음 명령어를 사용할 수 있어.

```bash
ros2 node list
```

예상 결과:

```text
/lesson_01_pose_subscriber
/turtlesim
```

실행 중인 다른 노드가 있다면 결과에 추가로 표시될 수 있어.

---

# 4. 핵심 코드: create_subscription()

이번 실습에서 가장 중요한 부분이야.

```python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10,
)
```

이 코드를 완전히 이해하면 다른 ROS 2 토픽도 구독할 수 있게 돼.

## 4-1. 인자 네 개 이해하기

`create_subscription()`의 인자 순서는 다음과 같아.

```python
self.create_subscription(
    메시지_타입,
    토픽_이름,
    콜백_함수,
    큐_크기,
)
```

각 인자의 의미를 살펴보자.

### 첫 번째: `Pose`

```python
Pose
```

구독할 메시지의 타입이야.

우리는 거북이의 위치 정보를 받을 것이므로 `Pose`를 사용해.

만약 메시지 타입이 다른 토픽을 구독한다면 해당 토픽의 메시지 타입에 맞게 바꿔야 해.

### 두 번째: `'/turtle1/pose'`

```python
'/turtle1/pose'
```

어떤 토픽을 구독할지 지정하는 부분이야.

우리는 첫 번째 거북이의 위치 정보를 받아야 하므로 `/turtle1/pose`를 사용해.

다음과 같이 이해하면 돼.

```text
/turtle1/pose
    │
    └── 첫 번째 거북이의 위치 정보
```

토픽 이름은 실제로 발행되는 이름과 일치해야 해.

참고로 `'/turtle1/pose'` 대신 `'turtle1/pose'`라고 작성해도 현재 네임스페이스가 루트라면 같은 토픽을 가리킬 수 있어. 초보 단계에서는 혼동을 줄이기 위해 절대 토픽 이름인 `'/turtle1/pose'`를 사용하는 것을 추천해.

### 세 번째: `self.on_pose`

```python
self.on_pose
```

메시지가 도착했을 때 실행할 함수를 지정하는 부분이야.

이 함수를 **콜백 함수(Callback Function)** 라고 불러.

우리가 작성한 다음 함수가 바로 콜백 함수야.

```python
def on_pose(self, msg):
```

예를 들어 거북이가 움직여서 새로운 위치 정보가 도착하면 ROS 2가 이 함수를 실행해.

```text
/turtle1/pose
       │
       │ 새 위치 메시지 도착
       ▼
   self.on_pose(msg)
       │
       ▼
   x, y, theta 출력
```

여기서 `self.on_pose`와 `self.on_pose()`는 다르다는 점에 주의해야 해.

- `self.on_pose`: 함수 자체를 전달
- `self.on_pose()`: 함수를 즉시 실행

`create_subscription()`에는 콜백 함수를 등록해야 하므로 괄호 없이 `self.on_pose`라고 작성하는 거야.

### 네 번째: `10`

```python
10
```

메시지를 처리하기 위해 사용하는 QoS 설정의 큐 깊이와 관련된 값이야.

이 코드에서는 정수 `10`을 전달하므로 ROS 2가 기본적인 구독 QoS 설정을 사용하면서 큐 깊이를 10으로 지정해.

쉽게 말하면, 메시지가 도착했는데 콜백이 바로 처리하지 못하는 경우를 대비해 대기시킬 메시지 수를 설정하는 거야.

다만 이 숫자가 항상 정확히 10개의 메시지를 보관한다는 의미로만 해석하면 안 돼. 실제 동작은 QoS 설정과 실행 상태 등에 영향을 받아.

**정리하면 다음과 같아.**

```python
self.subscription = self.create_subscription(
    Pose,                  # 어떤 데이터인가?
    '/turtle1/pose',        # 어디에서 받을 것인가?
    self.on_pose,           # 받으면 어떤 함수를 실행할 것인가?
    10,                     # 큐 깊이는 얼마인가?
)
```

---

# 5. 콜백 함수에서 데이터 출력하기

다음 코드를 살펴보자.

```python
def on_pose(self, msg):
    self.get_logger().info(
        f'x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
    )
```

## 5-1. `def on_pose(self, msg)`

```python
def on_pose(self, msg):
```

이 함수는 토픽에서 메시지가 전달될 때 실행돼.

여기서 `msg`는 메시지 객체야.

ROS 2가 `/turtle1/pose`에서 받은 데이터를 이 함수의 `msg` 인자로 전달해 주는 거야.

예를 들어 실제 메시지가 다음과 같다고 가정해 보자.

```text
x = 5.544445
y = 5.544445
theta = 0.0
```

그러면 함수 안에서 다음과 같이 접근할 수 있어.

```python
msg.x
msg.y
msg.theta
```

이 값들은 앞에서 확인했던 `Pose` 메시지의 필드야.

## 5-2. `msg.x`, `msg.y`, `msg.theta`

각각의 의미는 다음과 같아.

```python
msg.x
```

거북이의 가로 위치를 가져와.

```python
msg.y
```

거북이의 세로 위치를 가져와.

```python
msg.theta
```

거북이가 바라보는 방향각을 가져와.

여기서 중요한 점은 **`msg`는 우리가 직접 만든 변수가 아니라, ROS 2가 콜백에 전달하는 메시지 객체를 받기 위해 사용하는 매개변수**라는 거야.

변수 이름은 `msg` 대신 `pose`라고 작성해도 돼.

예를 들면 다음과 같이 작성할 수도 있어.

```python
def on_pose(self, pose):
    self.get_logger().info(
        f'x={pose.x:.2f}, y={pose.y:.2f}, theta={pose.theta:.2f}'
    )
```

두 코드는 기능적으로 같아.

## 5-3. `:.2f`의 의미

```python
f'x={msg.x:.2f}'
```

여기서 `:.2f`는 소수점 아래 두 자리까지 표시하라는 의미야.

예를 들어 다음 값이 있다고 해보자.

```python
msg.x = 5.544445
```

일반적으로 출력하면 다음과 같아.

```text
5.544445
```

하지만 `:.2f`를 사용하면 다음과 같이 출력돼.

```text
5.54
```

위치 값을 보기 편하게 정리해 주는 거야.

## 5-4. `self.get_logger().info()`

```python
self.get_logger().info('메시지')
```

ROS 2의 로그 기능을 사용해 정보를 출력하는 코드야.

일반적인 Python의 `print()`와 달리 ROS 2 로그에는 로그 수준이나 노드 관련 정보가 표시될 수 있어.

예를 들어 다음과 같이 작성할 수 있어.

```python
self.get_logger().info('거북이 위치를 수신했습니다.')
```

출력 예시:

```text
[INFO] [1760000000.123456789] [lesson_01_pose_subscriber]: 거북이 위치를 수신했습니다.
```

여기서 `[INFO]`는 정보 수준의 로그라는 뜻이야.

---

# 6. `rclpy.spin(node)`은 왜 필요할까?

이 부분도 매우 중요해.

```python
def main(args=None):
    rclpy.init(args=args)
    node = PoseSubscriber()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()
```

하나씩 살펴보자.

## 6-1. ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 기능을 초기화해.

ROS 2 노드를 사용하기 전에 실행해야 해.

## 6-2. 노드 생성

```python
node = PoseSubscriber()
```

앞에서 정의한 `PoseSubscriber` 클래스로 실제 노드를 생성해.

이때 초기화 함수인 `__init__()`이 실행되면서 `/turtle1/pose` 구독이 등록돼.

## 6-3. 노드 실행

```python
rclpy.spin(node)
```

이 코드는 노드가 메시지를 수신하고 콜백을 처리할 수 있도록 실행 상태를 유지해.

이해하기 쉽게 비교해 보자.

### `spin()`이 없는 경우

```python
rclpy.init(args=args)
node = PoseSubscriber()

node.destroy_node()
rclpy.shutdown()
```

노드를 생성한 뒤 곧바로 종료해 버려.

메시지를 계속 받아 처리할 기회가 없어지는 거야.

### `spin()`이 있는 경우

```python
rclpy.init(args=args)
node = PoseSubscriber()

rclpy.spin(node)

node.destroy_node()
rclpy.shutdown()
```

노드가 실행되는 동안 들어오는 메시지를 처리하고, 콜백 함수를 호출해.

```text
노드 생성
   │
   ▼
토픽 구독 등록
   │
   ▼
rclpy.spin(node)
   │
   ├── 메시지 수신 → on_pose() 실행
   ├── 메시지 수신 → on_pose() 실행
   ├── 메시지 수신 → on_pose() 실행
   └── 계속 반복
```

일반적인 단일 스레드 실행 환경에서 `rclpy.spin(node)`은 노드가 종료되거나 실행이 중단될 때까지 콜백을 처리해.

## 6-4. 노드 종료

```python
node.destroy_node()
rclpy.shutdown()
```

`node.destroy_node()`는 생성한 노드의 자원을 정리하고, `rclpy.shutdown()`은 ROS 2 실행 환경을 종료해.

일반적으로 `Ctrl + C`로 실행을 중단하면 `spin()`이 종료되고 이후 정리 코드가 실행돼.

---

# 7. 완성 코드

이제 앞에서 배운 내용을 합쳐 보자.

파일 경로:

```text
~/ros2_ws/src/turtle_robot/turtle_robot/lesson_01_pose_subscriber.py
```

아래 코드를 그대로 사용하면 돼.

```python
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    """거북이의 위치 정보를 구독하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_01_pose_subscriber')

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10,
        )

    def on_pose(self, msg):
        """거북이의 위치와 방향을 출력합니다."""
        self.get_logger().info(
            f'x={msg.x:.2f}, '
            f'y={msg.y:.2f}, '
            f'theta={msg.theta:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = PoseSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

마지막 부분을 조금 더 살펴보자.

```python
if __name__ == '__main__':
    main()
```

Python 파일을 직접 실행할 때 `main()`을 호출하는 코드야.

ROS 2의 `console_scripts`를 통해 실행하더라도 최종적으로는 등록한 `main()` 함수가 실행돼.

위 코드에서는 `try`, `except`, `finally`를 추가했어. `Ctrl + C`로 종료할 때 노드와 ROS 2 실행 환경을 정리하기 위한 일반적인 패턴이야.

---

# 8. `setup.py`와 `package.xml` 이해하기

Python 파일을 작성하는 것만으로는 다음 명령어로 실행할 수 없어.

```bash
ros2 run turtle_robot lesson_01_pose_subscriber
```

ROS 2가 실행할 수 있도록 패키지 설정을 해줘야 해.

## 8-1. setup.py

파일 경로:

```text
~/ros2_ws/src/turtle_robot/setup.py
```

다음 부분을 확인해.

```python
entry_points={
    'console_scripts': [
        'lesson_01_pose_subscriber = turtle_robot.lesson_01_pose_subscriber:main',
    ],
},
```

이 설정은 ROS 2에서 실행할 명령어와 실제 Python 코드를 연결해 줘.

구성 요소를 나눠 보자.

```text
lesson_01_pose_subscriber
          =
turtle_robot.lesson_01_pose_subscriber:main
```

| 부분 | 의미 |
|---|---|
| `lesson_01_pose_subscriber` | 터미널에서 실행할 명령어 이름 |
| `turtle_robot` | Python 패키지 이름 |
| `lesson_01_pose_subscriber` | Python 파일 이름에서 `.py`를 제외한 모듈 이름 |
| `main` | 실행할 함수 |

따라서 다음 명령어를 실행하면,

```bash
ros2 run turtle_robot lesson_01_pose_subscriber
```

ROS 2는 설정을 통해 `turtle_robot.lesson_01_pose_subscriber` 모듈의 `main()` 함수를 실행하게 돼.

여기서 주의할 점이 있어.

**실행 명령어 이름과 Python 파일 이름은 서로 달라도 돼.** 다만 `setup.py`에 적은 모듈 경로는 실제 파일 구조와 일치해야 해.

## 8-2. package.xml

파일 경로:

```text
~/ros2_ws/src/turtle_robot/package.xml
```

핵심 부분은 다음과 같아.

```xml
<depend>rclpy</depend>
<depend>turtlesim</depend>
```

각 항목의 의미는 다음과 같아.

| 항목 | 의미 |
|---|---|
| `rclpy` | Python에서 ROS 2 노드를 작성하기 위해 필요 |
| `turtlesim` | `turtlesim.msg.Pose` 메시지를 사용하기 위해 필요 |

`package.xml`은 패키지의 메타데이터와 의존성 등을 선언하는 파일이야.

다만 이 두 항목만 있다고 해서 ROS 2가 모든 파일을 자동으로 찾아주는 것은 아니야. 패키지 구조와 설치 설정도 올바르게 구성돼 있어야 해.

---

# 9. 빌드하고 실행하기

이제 실제로 실행해 보자.

최근 실습에서 `colcon` 명령어를 찾지 못하는 문제가 있었으니, 먼저 설치 여부부터 확인하자.

### ① colcon 확인

```bash
colcon --version
```

명령어를 찾을 수 없다고 나오면 다음을 실행해.

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions
```

### ② ROS 2 환경 불러오기

새 터미널을 열었다면 먼저 실행해.

```bash
source /opt/ros/jazzy/setup.bash
```

### ③ 워크스페이스로 이동

```bash
cd ~/ros2_ws
```

### ④ 패키지 빌드

```bash
colcon build --packages-select turtle_robot
```

빌드가 성공하면 다음과 비슷한 결과가 나와.

```text
Starting >>> turtle_robot
Finished <<< turtle_robot
Summary: 1 package finished
```

### ⑤ 빌드한 패키지 환경 적용

```bash
source install/setup.bash
```

이 명령어는 새 터미널을 열 때마다 해당 터미널에서 실행해야 해. 또는 `~/.bashrc`에 적절히 설정해 자동으로 적용할 수도 있어.

### ⑥ 노드 실행

`turtlesim_node`와 `turtle_teleop_key`가 실행 중인 상태에서 다음 명령어를 실행해.

```bash
ros2 run turtle_robot lesson_01_pose_subscriber
```

정상적으로 실행되면 거북이의 위치 정보가 터미널에 계속 출력돼.

예시:

```text
[INFO] [...] [lesson_01_pose_subscriber]: x=5.54, y=5.54, theta=0.00
[INFO] [...] [lesson_01_pose_subscriber]: x=5.54, y=5.54, theta=0.00
[INFO] [...] [lesson_01_pose_subscriber]: x=5.64, y=5.54, theta=0.00
```

거북이를 움직여서 출력값이 변하는지 확인해 봐.

참고로 구독 노드가 실행 중인데도 위치 값이 바뀌지 않는다면 다음 명령어로 토픽 상태를 확인할 수 있어.

```bash
ros2 topic info /turtle1/pose
```

또는 다음 명령어로 노드 목록을 확인해.

```bash
ros2 node list
```

---

# 10. 실습 코드를 이해했는지 확인하기

이번에는 코드를 외우는 것보다 각 코드가 왜 필요한지 이해하는 것이 중요해.

다음 다섯 가지 질문에 답할 수 있다면 이번 실습의 핵심을 잘 이해한 거야.

**질문 1.** 다음 코드에서 `Pose`는 어떤 역할을 할까?

```python
self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10,
)
```

**질문 2.** 다음 두 코드의 차이는 무엇일까?

```python
self.on_pose
```

```python
self.on_pose()
```

**질문 3.** 다음 코드에서 `msg.x`는 어떤 값을 의미할까?

```python
def on_pose(self, msg):
    print(msg.x)
```

**질문 4.** 다음 코드가 없다면 어떤 문제가 생길까?

```python
rclpy.spin(node)
```

**질문 5.** 다음 설정에서 `lesson_01_pose_subscriber`는 무엇을 의미할까?

```python
'lesson_01_pose_subscriber = turtle_robot.lesson_01_pose_subscriber:main',
```

---

## 이번 실습에서 꼭 기억할 4가지

1. **Topic**은 노드 간 데이터를 주고받는 통로야.
2. **Subscriber**는 토픽을 구독해서 데이터를 받는 노드야.
3. **Callback**은 메시지가 도착했을 때 실행되는 함수야.
4. **`rclpy.spin(node)`**은 노드가 콜백을 처리할 수 있도록 실행 상태를 유지해.

