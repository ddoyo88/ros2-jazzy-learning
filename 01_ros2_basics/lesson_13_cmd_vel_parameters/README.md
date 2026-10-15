
# 1. 이 프로그램은 무엇을 할까?

목표는 거북이가 원을 그리면서 움직이고, 시간이 지날수록 원의 크기를 키우는 거야.

거북이의 속도는 두 가지로 나뉘어.

- **선속도(Linear Velocity):** 앞으로 이동하는 속도
- **각속도(Angular Velocity):** 회전하는 속도

예를 들어 다음과 같이 설정한다고 생각해 보자.

| 시간 | 전진 속도 `linear_speed` | 회전 속도 `angular_speed` |
|---|---:|---:|
| 시작 | 1.0 | 1.0 |
| 다음 단계 | 1.5 | 1.0 |
| 그다음 단계 | 2.0 | 1.0 |
| 이후 | 2.5 | 1.0 |

전진 속도는 계속 커지고 회전 속도는 일정하게 유지돼.

이렇게 하면 거북이가 회전하는 동안 앞으로 더 빠르게 이동하게 되어, 점점 더 큰 원을 그릴 수 있어.

다만 실제 원의 크기와 모양은 선속도와 각속도의 비율에 따라 결정돼.

---

# 2. 전체 코드 살펴보기

네가 작성한 코드는 다음과 같아.

```python
"""거북이가 점점 큰 원을 그리게 하는 Publisher 실습입니다."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter


class CmdVelParameterPublisher(Node):
    """거북이 속도를 발행하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_13_cmd_vel_parameters')

        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)

        # /turtle1/cmd_vel에 Twist를 발행하는 Publisher
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 0.1초마다 publish_velocity 실행
        self.timer = self.create_timer(
            0.1,
            self.publish_velocity
        )

    def publish_velocity(self):
        """회전 속도를 유지하고 전진 속도를 높여 원을 키웁니다."""

        message = Twist()

        message.linear.x = self.get_parameter('linear_speed').value
        message.angular.z = self.get_parameter('angular_speed').value

        self.publisher.publish(message)


def main(args=None):
    """노드를 실행합니다."""

    rclpy.init(args=args)
    node = CmdVelParameterPublisher()

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

전체적인 실행 흐름은 다음과 같아.

```text
프로그램 시작
    ↓
ROS 2 초기화
    ↓
CmdVelParameterPublisher 노드 생성
    ↓
속도 파라미터 선언
    ↓
Publisher 생성
    ↓
Timer 생성
    ↓
0.1초마다 publish_velocity() 실행
    ↓
속도 파라미터 읽기
    ↓
Twist 메시지에 속도 설정
    ↓
/turtle1/cmd_vel로 발행
    ↓
거북이 이동
```

이제 각 부분을 자세히 알아보자.

# 3. 필요한 라이브러리 불러오기

```python
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
```

## 3-1. `Twist`

```python
from geometry_msgs.msg import Twist
```

`Twist`는 로봇의 선속도와 각속도를 표현하는 ROS 2 메시지 타입이야.

주요 필드는 다음과 같아.

| 필드 | 의미 |
|---|---|
| `linear.x` | x축 방향 선속도 |
| `linear.y` | y축 방향 선속도 |
| `linear.z` | z축 방향 선속도 |
| `angular.x` | x축 기준 각속도 |
| `angular.y` | y축 기준 각속도 |
| `angular.z` | z축 기준 각속도 |

`turtlesim`에서는 주로 다음 두 필드를 사용해.

```python
message.linear.x
message.angular.z
```

### `linear.x`

```python
message.linear.x = 1.0
```

거북이가 바라보는 방향으로 전진하는 속도를 설정해.

### `angular.z`

```python
message.angular.z = 1.0
```

거북이가 회전하는 속도를 설정해.

`turtlesim`에서 양수인 각속도는 일반적으로 반시계 방향 회전을 의미해.

따라서 두 값을 함께 설정하면 거북이가 전진하면서 회전하게 돼.

## 3-2. `rclpy`

```python
import rclpy
```

Python에서 ROS 2 기능을 사용하기 위한 라이브러리야.

이번 코드에서는 ROS 2를 초기화하고, 노드의 콜백을 처리하고, 종료하는 데 사용해.

## 3-3. `Node`

```python
from rclpy.node import Node
```

ROS 2 노드를 만들기 위해 사용하는 클래스야.

이번 코드에서는 `Node`를 상속받아 속도를 발행하는 노드를 만들고 있어.

## 3-4. `Parameter`

```python
from rclpy.parameter import Parameter
```

이 부분은 현재 코드에서 실제로 사용되지 않고 있어.

현재 파라미터를 선언하고 읽는 데 사용한 메서드는 다음과 같아.

```python
self.declare_parameter(...)
self.get_parameter(...)
```

따라서 지금 코드에서는 다음 줄을 삭제해도 돼.

```python
from rclpy.parameter import Parameter
```

나중에 `Parameter` 객체를 직접 만들거나 파라미터 타입을 명시하는 실습에서는 필요할 수 있어.

---

# 4. 클래스와 노드 초기화

```python
class CmdVelParameterPublisher(Node):
    """거북이 속도를 발행하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_13_cmd_vel_parameters')
```

## 4-1. 클래스 정의

```python
class CmdVelParameterPublisher(Node):
```

`CmdVelParameterPublisher`라는 클래스를 만들고, ROS 2의 `Node`를 상속받고 있어.

클래스 이름을 해석하면 다음과 같아.

- `CmdVel`: 속도 명령
- `Parameter`: 파라미터
- `Publisher`: 메시지를 발행하는 노드

즉, **파라미터로 속도를 설정해 속도 명령을 발행하는 노드**라는 의미야.

## 4-2. 노드 이름 설정

```python
super().__init__('lesson_13_cmd_vel_parameters')
```

ROS 2 노드의 이름을 설정해.

노드가 실행 중일 때 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

출력에는 다음과 비슷한 이름이 나타날 거야.

```text
/lesson_13_cmd_vel_parameters
```

---

# 5. ROS 2 Parameter란 무엇일까?

이번 실습에서 가장 중요한 개념이야.

다음 두 줄을 보자.

```python
self.declare_parameter('linear_speed', 1.0)
self.declare_parameter('angular_speed', 1.0)
```

여기서는 두 개의 파라미터를 선언하고 있어.

## 5-1. 파라미터의 의미

파라미터는 노드가 사용하는 설정값이야.

일반적인 Python 변수와 비교해 보자.

일반 변수는 다음과 같이 작성해.

```python
linear_speed = 1.0
```

반면 ROS 2 파라미터는 다음과 같이 선언해.

```python
self.declare_parameter('linear_speed', 1.0)
```

두 가지 모두 값을 저장한다는 점에서는 비슷하지만, ROS 2 파라미터는 ROS 2의 파라미터 시스템을 통해 조회하거나 변경할 수 있어.

예를 들어 실행 중인 노드의 속도를 터미널에서 변경할 수 있어.

```bash
ros2 param set /lesson_13_cmd_vel_parameters linear_speed 2.0
```

이렇게 하면 노드가 `linear_speed` 파라미터를 다시 읽을 때 변경된 값을 사용할 수 있어.

단, **파라미터를 변경하는 것과 코드에서 값을 자동으로 증가시키는 것은 다른 기능**이야. 현재 코드는 파라미터를 읽어 사용하지만, 스스로 값을 증가시키지는 않아.

## 5-2. `linear_speed` 선언

```python
self.declare_parameter('linear_speed', 1.0)
```

이 코드는 `linear_speed`라는 파라미터를 선언해.

초기값은 `1.0`이야.

이 파라미터는 거북이의 전진 속도를 설정하는 데 사용돼.

## 5-3. `angular_speed` 선언

```python
self.declare_parameter('angular_speed', 1.0)
```

이 코드는 `angular_speed`라는 파라미터를 선언해.

초기값은 `1.0`이야.

이 파라미터는 거북이의 회전 속도를 설정하는 데 사용돼.

두 파라미터를 정리하면 다음과 같아.

| 파라미터 | 초기값 | 용도 |
|---|---:|---|
| `linear_speed` | `1.0` | 전진 속도 |
| `angular_speed` | `1.0` | 회전 속도 |

---

# 6. Publisher 만들기

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

이 코드는 거북이에게 속도 명령을 보내기 위한 Publisher를 생성해.

일반적인 형식은 다음과 같아.

```python
self.create_publisher(메시지_타입, 토픽_이름, 큐_크기)
```

각 항목을 살펴보자.

| 코드 | 의미 |
|---|---|
| `Twist` | 발행할 메시지 타입 |
| `'/turtle1/cmd_vel'` | 발행할 토픽 |
| `10` | QoS 설정의 메시지 큐 깊이 |

## `/turtle1/cmd_vel`은 무엇일까?

이 토픽은 `turtle1`에 속도 명령을 전달하는 데 사용돼.

예를 들어 다음과 같은 메시지를 발행하면 거북이가 움직여.

```python
message = Twist()
message.linear.x = 1.0
message.angular.z = 1.0

self.publisher.publish(message)
```

이 코드는 전진 속도와 회전 속도를 모두 지정해서 거북이가 전진하면서 회전하도록 해.

전체 구조는 다음과 같아.

```text
CmdVelParameterPublisher
          │
          │ Twist 메시지 발행
          ▼
 /turtle1/cmd_vel
          │
          ▼
      turtlesim
          │
          ▼
       turtle1 이동
```

---

# 7. Timer 만들기

```python
self.timer = self.create_timer(
    0.1,
    self.publish_velocity
)
```

Timer는 정해진 시간 간격으로 콜백 함수를 실행하는 기능이야.

여기서는 `0.1`초마다 `publish_velocity()`를 실행해.

## 7-1. `0.1`은 무슨 뜻일까?

```python
self.create_timer(0.1, self.publish_velocity)
```

첫 번째 인수인 `0.1`은 초 단위의 시간 간격이야.

따라서 약 0.1초마다 콜백이 실행되도록 요청하는 거야.

계산해 보면 다음과 같아.

\[
\frac{1}{0.1}=10
\]

즉, 이상적으로는 초당 10회 실행되는 간격이야.

실제 실행 빈도는 운영체제의 스케줄링이나 노드의 처리 상황에 따라 달라질 수 있어.

## 7-2. `self.publish_velocity`

```python
self.publish_velocity
```

여기에는 함수 이름만 전달하고 있어.

이렇게 하면 Timer가 지정한 시간 간격마다 함수를 실행할 수 있어.

다음처럼 괄호를 붙이면 안 돼.

```python
self.publish_velocity()
```

괄호를 붙이면 함수를 그 자리에서 바로 호출한다는 의미가 되기 때문이야.

이번 코드에서는 함수를 Timer의 콜백으로 등록해야 하므로 괄호 없이 전달하는 거야.

---

# 8. `publish_velocity()` 함수 자세히 살펴보기

이제 실제 속도 명령을 만드는 부분이야.

```python
def publish_velocity(self):
    """회전 속도를 유지하고 전진 속도를 높여 원을 키웁니다."""

    message = Twist()

    message.linear.x = self.get_parameter('linear_speed').value
    message.angular.z = self.get_parameter('angular_speed').value

    self.publisher.publish(message)
```

이 함수는 다음 순서로 실행돼.

1. `Twist` 메시지를 생성해.
2. 전진 속도 파라미터를 읽어.
3. 회전 속도 파라미터를 읽어.
4. 메시지를 발행해.

하나씩 살펴보자.

## 8-1. Twist 메시지 생성

```python
message = Twist()
```

속도 명령을 담을 새로운 메시지 객체를 만드는 코드야.

이제 `message` 객체에 속도값을 넣을 수 있어.

예를 들어 다음과 같이 작성할 수 있어.

```python
message.linear.x = 1.0
message.angular.z = 0.5
```

이 경우 전진 속도는 `1.0`, 회전 속도는 `0.5`가 돼.

## 8-2. 전진 속도 파라미터 읽기

```python
message.linear.x = self.get_parameter('linear_speed').value
```

이 코드를 세 부분으로 나눠 보자.

### 첫 번째: `self.get_parameter()`

```python
self.get_parameter('linear_speed')
```

`linear_speed`라는 이름의 파라미터를 가져와.

### 두 번째: `.value`

```python
self.get_parameter('linear_speed').value
```

파라미터 객체에서 실제 값을 가져오는 부분이야.

예를 들어 파라미터 값이 `1.0`이면 결과는 `1.0`이야.

### 세 번째: 메시지에 저장

```python
message.linear.x = self.get_parameter('linear_speed').value
```

가져온 값을 메시지의 전진 속도 필드에 저장해.

초기값이 `1.0`이므로 다음과 같은 결과가 돼.

```python
message.linear.x = 1.0
```

## 8-3. 회전 속도 파라미터 읽기

```python
message.angular.z = self.get_parameter('angular_speed').value
```

이번에는 `angular_speed` 파라미터를 읽어 회전 속도를 지정해.

초기값이 `1.0`이므로 다음과 같은 결과가 돼.

```python
message.angular.z = 1.0
```

따라서 현재 메시지는 다음과 같은 상태야.

```python
message.linear.x = 1.0
message.angular.z = 1.0
```

## 8-4. 메시지 발행하기

```python
self.publisher.publish(message)
```

완성한 `Twist` 메시지를 `/turtle1/cmd_vel` 토픽으로 발행해.

이 메시지를 받은 `turtlesim`은 해당 속도 명령에 따라 거북이를 움직여.

여기까지가 현재 코드에서 속도 명령을 발행하는 전체 과정이야.

---

# 9. 그런데 왜 아직 원이 커지지 않을까?

여기서 네 코드의 중요한 부분을 확인해 보자.

현재 전진 속도는 다음과 같이 설정돼 있어.

```python
message.linear.x = self.get_parameter('linear_speed').value
```

초기 파라미터 값은 다음과 같아.

```python
self.declare_parameter('linear_speed', 1.0)
```

현재 코드는 Timer가 실행될 때마다 같은 파라미터를 읽고 있어.

따라서 파라미터를 별도로 변경하지 않는다면 전진 속도는 계속 `1.0`이야.

회전 속도도 마찬가지야.

```python
self.declare_parameter('angular_speed', 1.0)
```

따라서 현재 상태에서는 다음과 같은 명령을 반복해서 발행해.

```python
message.linear.x = 1.0
message.angular.z = 1.0
```

이 상태에서는 일정한 속도 비율로 움직이므로 일정한 크기의 원을 그리는 동작에 가까워.

**점점 큰 원을 그리려면 전진 속도를 시간에 따라 증가시키는 로직을 추가해야 해.**

---

# 10. 점점 큰 원을 그리도록 코드 수정하기

현재 실습의 의도를 구현하려면 전진 속도를 조금씩 증가시키면 돼.

예를 들어 0.1초마다 전진 속도를 `0.01`씩 높이는 방식이야.

먼저 `__init__()`에서 다음 변수를 추가해.

```python
self.linear_speed = 1.0
self.speed_increment = 0.01
```

그리고 `publish_velocity()`를 다음과 같이 수정해.

```python
def publish_velocity(self):
    """회전 속도를 유지하고 전진 속도를 높여 원을 키웁니다."""

    message = Twist()

    # 현재 파라미터 값을 읽습니다.
    self.linear_speed = self.get_parameter('linear_speed').value
    angular_speed = self.get_parameter('angular_speed').value

    # 현재 속도로 메시지를 작성합니다.
    message.linear.x = self.linear_speed
    message.angular.z = angular_speed

    # 속도 명령을 발행합니다.
    self.publisher.publish(message)

    # 다음 호출에서 사용할 전진 속도를 높입니다.
    self.linear_speed += self.speed_increment

    # 증가한 속도를 ROS 2 파라미터에 반영합니다.
    self.set_parameters([
        rclpy.parameter.Parameter(
            'linear_speed',
            rclpy.parameter.Parameter.Type.DOUBLE,
            self.linear_speed
        )
    ])
```

이 코드는 매번 파라미터를 읽은 뒤 속도를 증가시키고, 증가한 값을 다시 파라미터에 저장해.

다만 이 방식은 속도가 계속 증가해서 거북이가 지나치게 빨라질 수 있어. 실제로 사용할 때는 최대 속도를 설정하는 편이 좋아.

예를 들어 다음과 같이 제한할 수 있어.

```python
self.linear_speed = min(
    self.linear_speed + self.speed_increment,
    3.0
)
```

이렇게 하면 전진 속도가 `3.0`을 넘지 않게 할 수 있어.

### 더 간단한 방법

실습 목표가 단순히 전진 속도를 점점 높이는 것이라면, 속도 증가를 파라미터 자체에 반영하지 않고 별도 변수로 관리해도 돼.

예를 들어 다음과 같이 작성할 수 있어.

```python
def __init__(self):
    super().__init__('lesson_13_cmd_vel_parameters')

    self.declare_parameter('linear_speed', 1.0)
    self.declare_parameter('angular_speed', 1.0)

    self.current_linear_speed = 1.0

    self.publisher = self.create_publisher(
        Twist,
        '/turtle1/cmd_vel',
        10
    )

    self.timer = self.create_timer(
        0.1,
        self.publish_velocity
    )

def publish_velocity(self):
    """전진 속도를 조금씩 높입니다."""

    message = Twist()

    message.linear.x = self.current_linear_speed
    message.angular.z = self.get_parameter('angular_speed').value

    self.publisher.publish(message)

    self.current_linear_speed = min(
        self.current_linear_speed + 0.01,
        3.0
    )
```

이 방식은 현재 속도를 일반 Python 변수로 관리해. 다만 `linear_speed` 파라미터를 실행 중에 바꿔도 `current_linear_speed`가 자동으로 변경되지는 않는다는 차이가 있어.

따라서 **실행 중에 파라미터로 속도를 조절하는 것이 목표라면 파라미터를 기준으로 설계하고, 시간에 따라 속도를 변화시키는 것이 목표라면 별도 변수를 이용하는 방식**을 구분해서 이해하면 좋아.

---

# 11. `main()` 함수

```python
def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = CmdVelParameterPublisher()
```

이 부분은 노드를 실행하기 위한 기본 구조야.

### ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2를 초기화해.

### 노드 생성

```python
node = CmdVelParameterPublisher()
```

앞에서 정의한 클래스를 이용해 노드를 생성해.

이때 `__init__()`이 실행되면서 파라미터, Publisher, Timer가 설정돼.

## 11-1. `rclpy.spin(node)`

```python
try:
    rclpy.spin(node)
```

노드가 계속 이벤트를 처리하도록 해.

이 코드가 없으면 Timer 콜백이 정상적으로 실행되지 않아.

이번 실습에서는 Timer가 0.1초마다 `publish_velocity()`를 실행해야 하므로 `spin()`이 필요해.

## 11-2. 종료 처리

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

`Ctrl + C`로 프로그램을 종료하면 정리 작업을 수행해.

- `node.destroy_node()`: 노드 정리
- `rclpy.try_shutdown()`: ROS 2 종료 시도

이 패턴은 앞에서 배운 Publisher와 Service 실습에서도 동일하게 사용했어.

---

# 12. Ubuntu에서 실행하는 방법

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 환경 기준이야.

### 터미널 1: turtlesim 실행

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

### 터미널 2: 패키지 빌드

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 완료되면 다음 명령어를 실행해.

```bash
source install/setup.bash
```

그리고 노드를 실행해.

```bash
ros2 run turtle_robot lesson_13_cmd_vel_parameters
```

단, 이 명령어가 동작하려면 `setup.py`에 해당 실행 항목이 등록되어 있어야 해.

### 실행 중 파라미터 확인

새 터미널을 열고 다음을 실행해.

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

현재 노드의 파라미터 목록을 확인해.

```bash
ros2 param list /lesson_13_cmd_vel_parameters
```

파라미터 값을 확인하려면 다음 명령어를 사용해.

```bash
ros2 param get /lesson_13_cmd_vel_parameters linear_speed
```

회전 속도도 확인할 수 있어.

```bash
ros2 param get /lesson_13_cmd_vel_parameters angular_speed
```

실행 중 전진 속도를 변경하려면 다음 명령어를 입력해.

```bash
ros2 param set /lesson_13_cmd_vel_parameters linear_speed 2.0
```

회전 속도를 변경하려면 다음과 같이 입력해.

```bash
ros2 param set /lesson_13_cmd_vel_parameters angular_speed 0.5
```

현재 코드는 매번 파라미터를 읽으므로 변경된 값이 다음 Timer 실행부터 사용돼.

단, 이 명령어로 파라미터를 변경하는 것만으로 속도가 자동으로 계속 증가하는 것은 아니야.

---

# 13. 이번 실습에서 기억해야 할 핵심

| 코드 | 핵심 개념 |
|---|---|
| `declare_parameter()` | ROS 2 파라미터 선언 |
| `get_parameter().value` | 파라미터 값 읽기 |
| `create_publisher()` | 메시지를 발행할 Publisher 생성 |
| `create_timer(0.1, ...)` | 0.1초 간격으로 콜백 실행 |
| `Twist()` | 속도 메시지 생성 |
| `publish(message)` | 속도 명령 발행 |
| `rclpy.spin(node)` | 노드의 이벤트 처리 유지 |

이번 실습에서 특히 중요한 것은 **파라미터와 일반 변수의 차이**야.

- 파라미터는 ROS 2 도구를 통해 조회하고 변경할 수 있는 설정값이야.
- 일반 변수는 Python 코드 내부에서 상태를 저장하거나 계산하는 데 사용해.
- Timer는 정해진 간격으로 콜백을 실행해.
- Publisher는 계산한 속도 명령을 다른 노드에 전달해.

이 네 가지를 연결하면 실행 중 속도를 조절하는 로봇 제어 프로그램을 만들 수 있어.

그리고 현재 네 코드에서 수정해야 할 핵심은 하나야.
