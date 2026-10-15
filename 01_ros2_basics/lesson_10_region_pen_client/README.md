
# 1. 이 코드는 무엇을 할까?

코드를 실행하면 거북이가 화면의 왼쪽 영역에 있는지 오른쪽 영역에 있는지 확인해.

- **왼쪽 영역:** 노란색 펜
- **오른쪽 영역:** 초록색 펜

화면의 가로 좌표인 `x`를 기준으로 영역을 구분해.

```python
if message.x < 5.0:
    new_region = 'left'
else:
    new_region = 'right'
```

즉, `x`가 5.0보다 작으면 왼쪽이고, 5.0 이상이면 오른쪽이야.

`turtlesim` 화면에서 다음과 같은 동작을 한다고 생각하면 돼.

```text
                  x = 5.0
                     │
       왼쪽 영역      │      오른쪽 영역
                     │
       🐢 ──────────→│
                     │
       펜 색상: 노랑  │      펜 색상: 초록
                     │
```

실제로는 거북이가 이동할 때마다 위치 정보가 전달되고, 영역이 바뀌면 서비스가 호출되어 펜 색상이 변경돼.

**중요한 점은 거북이의 위치가 바뀔 때마다 무조건 서비스를 호출하는 것이 아니라, 왼쪽과 오른쪽 영역이 바뀌었을 때만 호출한다는 거야.**

이제 코드의 원리를 살펴보자.

---

# 2. 필요한 라이브러리 불러오기

```python
"""위치에 따라 펜 색상을 바꾸는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose  # noqa: F401
from turtlesim.srv import SetPen  # noqa: F401
```

각 코드의 역할은 다음과 같아.

## 2-1. `rclpy`

```python
import rclpy
```

Python에서 ROS 2 기능을 사용하기 위한 라이브러리야.

이번 코드에서는 다음 기능을 사용해.

```python
rclpy.init(args=args)
rclpy.spin(node)
rclpy.try_shutdown()
```

각각 ROS 2 초기화, 노드의 이벤트 처리, ROS 2 종료를 담당해.

## 2-2. `Node`

```python
from rclpy.node import Node
```

ROS 2 노드를 만들기 위해 가져오는 클래스야.

이번 실습에서는 거북이의 위치를 구독하고, 펜 색상 변경 서비스를 호출하는 노드를 만들 거야.

## 2-3. `Pose`

```python
from turtlesim.msg import Pose  # noqa: F401
```

`Pose`는 거북이의 현재 위치와 방향을 전달하는 메시지 타입이야.

주요 필드는 다음과 같아.

| 필드 | 의미 |
|---|---|
| `x` | 거북이의 가로 위치 |
| `y` | 거북이의 세로 위치 |
| `theta` | 거북이가 바라보는 방향 |
| `linear_velocity` | 선속도 |
| `angular_velocity` | 각속도 |

이번 실습에서는 이 중 `x`만 사용해.

예를 들어 위치 메시지가 다음과 같다고 해보자.

```python
message.x = 3.0
message.y = 4.0
message.theta = 0.0
```

이때 `message.x`는 거북이의 가로 좌표인 `3.0`을 의미해.

따라서 다음 조건은 참이 돼.

```python
message.x < 5.0
```

그 결과 거북이는 왼쪽 영역에 있다고 판단해.

## 2-4. `SetPen`

```python
from turtlesim.srv import SetPen  # noqa: F401
```

`SetPen`은 거북이의 펜 설정을 변경하는 서비스 타입이야.

펜의 색상이나 굵기, 펜을 내릴지 올릴지를 지정할 수 있어.

주요 요청 필드는 다음과 같아.

| 필드 | 의미 |
|---|---|
| `r` | 빨간색 값 |
| `g` | 초록색 값 |
| `b` | 파란색 값 |
| `width` | 펜 굵기 |
| `off` | 펜을 끌지 여부 |

RGB 값은 각각 0부터 255까지 지정할 수 있어.

이번 실습에서는 `r`, `g`, `b`를 사용해서 색상을 변경할 거야.

---

# 3. RegionPenClient 클래스 만들기

```python
class RegionPenClient(Node):
    """왼쪽과 오른쪽 영역의 펜 색상을 바꾸는 노드입니다."""
```

`RegionPenClient`라는 클래스를 정의하고 있어.

```python
class RegionPenClient(Node):
```

여기서 `Node`를 상속받았기 때문에 ROS 2 노드에서 사용하는 기능을 활용할 수 있어.

이 노드는 크게 두 가지 역할을 해.

1. `/turtle1/pose`를 구독해서 거북이의 현재 위치를 확인해.
2. `/turtle1/set_pen` 서비스를 호출해서 펜 색상을 변경해.

이 두 기능을 결합하면 위치에 따라 색상을 자동으로 바꾸는 프로그램을 만들 수 있어.

---

# 4. `__init__()`에서 노드 초기화하기

```python
def __init__(self):
    super().__init__('lesson_10_region_pen_client')
    self.current_region = None
```

## 4-1. 노드 이름 설정

```python
super().__init__('lesson_10_region_pen_client')
```

부모 클래스인 `Node`의 초기화 기능을 호출하고 노드 이름을 지정해.

노드 이름은 다음과 같아.

```text
lesson_10_region_pen_client
```

이 이름은 ROS 2에서 노드를 확인할 때 사용돼.

실행 중 다음 명령어를 입력하면 확인할 수 있어.

```bash
ros2 node list
```

## 4-2. `current_region = None`

```python
self.current_region = None
```

이번 코드에서 매우 중요한 변수야.

`current_region`은 거북이가 마지막으로 판단된 어느 영역에 있었는지를 저장해.

가능한 값은 다음과 같아.

| 값 | 의미 |
|---|---|
| `None` | 아직 영역을 판단하지 않음 |
| `'left'` | 왼쪽 영역 |
| `'right'` | 오른쪽 영역 |

처음에는 아직 영역을 판단하지 않았으므로 `None`으로 초기화해.

왜 이 변수가 필요할까?

거북이가 왼쪽 영역에 있는 동안 위치 정보는 계속 전달돼.

예를 들어 거북이가 왼쪽에서 움직이면 다음과 같은 좌표가 전달될 수 있어.

```text
x = 2.0
x = 2.1
x = 2.2
x = 2.3
x = 2.4
```

이때 매번 서비스를 호출하면 불필요한 요청이 계속 발생해.

따라서 현재 영역을 기억하고 있다가 **영역이 바뀌었을 때만 펜 색상을 변경하도록** 만드는 거야.

이 원리는 센서값에 따라 동작을 바꾸는 로봇 프로그램에서도 자주 사용돼.

---

# 5. `/turtle1/set_pen` 서비스 클라이언트 생성

```python
self.client = self.create_client(SetPen, '/turtle1/set_pen')
```

이 코드는 펜 색상을 변경하는 서비스 클라이언트를 생성해.

형식은 다음과 같아.

```python
self.create_client(서비스_타입, 서비스_이름)
```

이번 코드에서는 다음과 같이 사용했어.

```python
self.create_client(SetPen, '/turtle1/set_pen')
```

각 부분의 의미를 살펴보자.

| 코드 | 의미 |
|---|---|
| `SetPen` | 서비스 요청과 응답의 타입 |
| `'/turtle1/set_pen'` | 호출할 서비스의 이름 |
| `self.client` | 생성한 클라이언트를 저장하는 변수 |

`turtlesim`은 `/turtle1/set_pen` 서비스를 제공해.

이 서비스를 호출하면 `turtle1`의 펜 설정을 변경할 수 있어.

전체적인 흐름은 다음과 같아.

```text
RegionPenClient
       │
       │ 펜 색상 변경 요청
       ▼
/turtle1/set_pen
       │
       ▼
turtlesim
       │
       ▼
turtle1의 펜 설정 변경
```

여기서 주의할 점이 있어.

**클라이언트를 생성하는 것과 서비스를 호출하는 것은 서로 다른 작업이야.**

이 코드는 서비스를 호출할 준비를 하는 단계일 뿐이야.

실제 호출은 아래에서 설명할 `call_set_pen_service()` 메서드에서 이루어져.

---

# 6. `/turtle1/pose` 토픽 구독하기

```python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

이 부분은 이번 실습의 또 다른 핵심이야.

거북이의 현재 위치를 알아내기 위해 `/turtle1/pose` 토픽을 구독하고 있어.

## 6-1. `create_subscription()`의 구조

일반적인 형식은 다음과 같아.

```python
self.create_subscription(
    메시지_타입,
    토픽_이름,
    콜백_함수,
    큐_크기
)
```

각 항목의 의미를 살펴보자.

| 코드 | 의미 |
|---|---|
| `Pose` | 수신할 메시지의 타입 |
| `'/turtle1/pose'` | 구독할 토픽 |
| `self.on_pose` | 메시지를 받았을 때 실행할 함수 |
| `10` | QoS 설정의 일부인 정수 깊이 |

### 첫 번째 인수: `Pose`

```python
Pose
```

거북이의 위치와 방향 정보를 담고 있는 메시지 타입이야.

ROS 2에서는 토픽마다 정해진 메시지 타입을 사용해.

예를 들어 다음과 같아.

| 토픽 | 메시지 타입 |
|---|---|
| `/turtle1/pose` | `turtlesim/msg/Pose` |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |

`/turtle1/pose`에서는 `Pose` 메시지를 사용하므로 첫 번째 인수에 `Pose`를 지정한 거야.

### 두 번째 인수: 토픽 이름

```python
'/turtle1/pose'
```

`turtle1`의 현재 위치 정보를 전달하는 토픽이야.

거북이가 이동하면 위치와 방향이 변경되고, 이 정보가 토픽을 통해 전달돼.

### 세 번째 인수: 콜백 함수

```python
self.on_pose
```

여기가 매우 중요해.

콜백 함수는 **특정 이벤트가 발생했을 때 자동으로 실행되는 함수**야.

이번 코드에서는 새로운 위치 메시지가 전달되면 `on_pose()`가 실행돼.

여기서 주의할 점은 다음과 같이 괄호를 붙이지 않는다는 거야.

```python
self.on_pose
```

이렇게 함수 이름만 전달하면 함수 자체를 콜백으로 등록할 수 있어.

반면 다음과 같이 작성하면 함수를 그 자리에서 호출하려는 표현이 돼.

```python
self.on_pose()
```

이번 실습에서는 위치 메시지가 수신될 때마다 실행되어야 하므로 `self.on_pose`를 전달해야 해.

### 네 번째 인수: `10`

```python
10
```

구독의 QoS 설정에서 메시지 큐의 깊이와 관련된 값이야.

간단히 말하면 메시지 처리가 지연될 때 대기할 수 있는 메시지의 개수를 설정하는 데 사용돼.

---

# 7. `on_pose()` 함수 자세히 알아보기

```python
def on_pose(self, message):
    """현재 위치에 맞는 펜 색상을 요청합니다."""
```

이 함수는 위치 메시지가 들어올 때마다 자동으로 실행돼.

여기서 `message`에는 수신한 `Pose` 메시지가 전달돼.

예를 들어 거북이의 현재 위치가 다음과 같다면,

```text
x = 3.0
y = 4.0
```

`message.x`는 `3.0`, `message.y`는 `4.0`이 되는 거야.

이번 실습에서는 `message.x`를 사용해서 영역을 판단할 거야.

---

# 8. 거북이의 위치를 왼쪽과 오른쪽으로 구분하기

```python
if message.x < 5.0:
    new_region = 'left'
else:
    new_region = 'right'
```

이 코드는 현재 위치에 따라 영역을 구분해.

## 8-1. 조건문 이해하기

```python
if message.x < 5.0:
```

`message.x`가 `5.0`보다 작은지 확인하는 조건이야.

참이면 아래 코드가 실행돼.

```python
new_region = 'left'
```

즉, 왼쪽 영역이라고 판단하는 거야.

반대로 `x`가 `5.0` 이상이면 `else` 블록이 실행돼.

```python
else:
    new_region = 'right'
```

오른쪽 영역이라고 판단하는 거야.

## 8-2. 실제 예시

| `message.x` | 판단 결과 |
|---:|---|
| `1.0` | `left` |
| `3.5` | `left` |
| `4.9` | `left` |
| `5.0` | `right` |
| `7.0` | `right` |
| `10.0` | `right` |

여기서 중요한 것은 **`x = 5.0`도 오른쪽 영역으로 분류된다는 것**이야.

왼쪽 조건이 `< 5.0`이기 때문이지.

만약 `x = 5.0`을 왼쪽에 포함하고 싶다면 조건을 다음과 같이 변경해야 해.

```python
if message.x <= 5.0:
```

하지만 현재 실습의 기준에서는 기존 코드가 맞아.

---

# 9. 이전과 같은 영역이면 서비스를 호출하지 않기

```python
if new_region == self.current_region:
    return
```

이 코드는 효율적인 ROS 2 프로그램을 만들기 위한 중요한 부분이야.

앞에서 `self.current_region`은 현재 영역을 기억하는 변수라고 설명했지?

이 코드는 새로 판단한 영역과 기존에 기억한 영역이 같은지 비교해.

## 9-1. `==`의 의미

```python
new_region == self.current_region
```

두 값이 같은지 확인하는 비교 연산자야.

예를 들어 다음과 같다고 해보자.

```python
new_region = 'left'
self.current_region = 'left'
```

두 값이 같으므로 조건이 참이 돼.

## 9-2. `return`의 의미

```python
return
```

현재 함수를 즉시 종료하는 명령어야.

따라서 같은 영역에 계속 머무르고 있으면 이후 코드가 실행되지 않아.

그 결과 펜 색상 변경 서비스를 호출하지 않게 돼.

## 9-3. 왜 필요할까?

이 부분이 없다면 거북이가 왼쪽 영역에서 이동하는 동안 위치 메시지를 받을 때마다 펜 색상 변경 요청을 보낼 수 있어.

예를 들어 다음과 같은 상황이 발생할 수 있어.

```text
위치 메시지 수신
    ↓
x = 2.0 → 왼쪽
    ↓
노란색 변경 요청

위치 메시지 수신
    ↓
x = 2.1 → 왼쪽
    ↓
노란색 변경 요청

위치 메시지 수신
    ↓
x = 2.2 → 왼쪽
    ↓
노란색 변경 요청
```

펜이 이미 노란색인데도 같은 요청을 계속 보내는 거야.

하지만 현재 코드에서는 이렇게 동작해.

```text
첫 번째 위치 메시지
    ↓
왼쪽 영역으로 판단
    ↓
이전 영역은 None
    ↓
영역이 바뀌었으므로 서비스 호출
    ↓
current_region = 'left'
```

이후 다시 왼쪽 영역에 있는 동안에는 다음과 같이 돼.

```text
다음 위치 메시지
    ↓
왼쪽 영역으로 판단
    ↓
이전 영역도 left
    ↓
두 값이 같음
    ↓
return
    ↓
서비스 호출하지 않음
```

그러다가 거북이가 오른쪽 영역으로 이동하면,

```text
위치 메시지 수신
    ↓
x = 6.0 → 오른쪽
    ↓
이전 영역은 left
    ↓
영역이 바뀌었음
    ↓
초록색 변경 서비스 호출
```

이런 방식으로 불필요한 서비스 호출을 줄일 수 있어.

---

# 10. 현재 영역을 저장하기

```python
self.current_region = new_region
```

이 코드는 새롭게 판단한 영역을 `current_region`에 저장해.

예를 들어 다음과 같아.

```python
new_region = 'left'
self.current_region = new_region
```

실행 후에는 다음과 같은 상태가 돼.

```python
self.current_region == 'left'
```

이후 새로운 위치 메시지가 도착하면 현재 영역과 비교할 수 있어.

여기서 **영역을 저장하는 것과 펜 색상을 변경하는 것은 서로 다른 작업**이라는 점을 기억하면 좋아.

- `self.current_region = new_region`: 현재 영역을 기억
- `self.call_set_pen_service(new_region)`: 해당 영역에 맞는 펜 색상 변경을 요청

따라서 다음 코드가 이어서 실행되는 거야.

```python
self.call_set_pen_service(new_region)
```

---

# 11. 펜 색상을 변경하는 함수

```python
def call_set_pen_service(self, region):
    """펜 색상을 변경하는 서비스를 호출합니다."""
```

이 함수는 전달받은 `region` 값에 따라 색상을 결정하고, 서비스 요청을 보내는 역할을 해.

앞에서는 영역을 판단했지?

이제 그 영역에 맞는 색상을 지정하는 거야.

```python
self.call_set_pen_service(new_region)
```

예를 들어 `new_region`이 `'left'`라면 다음과 같이 호출돼.

```python
self.call_set_pen_service('left')
```

그러면 `call_set_pen_service()`의 매개변수인 `region`에 `'left'`가 전달돼.

---

# 12. SetPen 요청 메시지 만들기

```python
req = SetPen.Request()
```

`SetPen` 서비스의 요청 객체를 만드는 코드야.

앞에서 배운 `Spawn.Request()`와 같은 원리야.

다만 서비스 타입이 다르기 때문에 요청에 포함되는 필드도 달라.

비교하면 다음과 같아.

| 서비스 | 요청 객체 | 주요 필드 |
|---|---|---|
| 거북이 생성 | `Spawn.Request()` | `x`, `y`, `theta`, `name` |
| 펜 설정 변경 | `SetPen.Request()` | `r`, `g`, `b`, `width`, `off` |

이번 실습에서는 `r`, `g`, `b`를 지정해서 색상을 바꿀 거야.

---

# 13. 왼쪽 영역에서는 노란색으로 변경하기

```python
if region == 'left':
    req.r = 255
    req.g = 255
    req.b = 0
```

이 코드는 `region`이 `'left'`인지 확인해.

왼쪽 영역이면 다음과 같은 RGB 값을 지정해.

```python
req.r = 255
req.g = 255
req.b = 0
```

RGB는 Red, Green, Blue의 약자야.

각 색상의 값은 일반적으로 0부터 255까지 지정해.

| 색상 | R | G | B |
|---|---:|---:|---:|
| 빨강 | 255 | 0 | 0 |
| 초록 | 0 | 255 | 0 |
| 파랑 | 0 | 0 | 255 |
| 노랑 | 255 | 255 | 0 |
| 흰색 | 255 | 255 | 255 |
| 검정 | 0 | 0 | 0 |

노란색은 빨간색과 초록색을 최대로 섞고, 파란색은 사용하지 않는 방식이야.

따라서 다음과 같이 지정하면 돼.

```python
req.r = 255
req.g = 255
req.b = 0
```

---

# 14. 오른쪽 영역에서는 초록색으로 변경하기

```python
elif region == 'right':
    req.r = 0
    req.g = 255
    req.b = 0
```

`elif`는 앞의 `if` 조건이 거짓일 때 다음 조건을 확인하는 문법이야.

여기서는 `region`이 `'right'`인지 확인해.

오른쪽 영역이라면 다음 RGB 값을 지정해.

```python
req.r = 0
req.g = 255
req.b = 0
```

초록색은 빨간색과 파란색을 사용하지 않고 초록색 값만 최대로 지정하는 거야.

```text
R = 0
G = 255
B = 0
```

따라서 왼쪽 영역에서는 노란색, 오른쪽 영역에서는 초록색을 사용하게 돼.

---

# 15. 서비스 요청 보내기

```python
self.client.call_async(req)
```

이제 작성한 펜 설정 요청을 서비스에 전달해.

앞에서 생성한 클라이언트는 다음과 같았지?

```python
self.client = self.create_client(SetPen, '/turtle1/set_pen')
```

따라서 다음 코드는 `/turtle1/set_pen` 서비스로 요청을 전송하는 거야.

```python
self.client.call_async(req)
```

`call_async()`는 비동기 방식으로 서비스를 호출해.

즉, 요청을 보내고 서비스 응답을 기다리는 동안 프로그램 전체가 그 자리에서 동기적으로 멈춰 있는 방식은 아니야.

이번 코드에서는 반환되는 `Future` 객체를 따로 저장하거나 응답을 확인하지 않고 있어.

색상 변경 요청 자체는 전송하지만, 서비스 호출이 정상적으로 완료됐는지까지 확인하고 싶다면 다음과 같이 작성할 수 있어.

```python
future = self.client.call_async(req)
```

이후 `future`가 완료되었을 때 결과를 확인하는 로직을 추가하면 돼.

다만 이번 실습의 핵심은 **위치 메시지를 받아 영역을 판단하고, 필요한 경우에만 펜 색상 변경 서비스를 호출하는 것**이므로 현재 구조로도 핵심 동작을 이해할 수 있어.

---

# 16. `main()` 함수 살펴보기

```python
def main(args=None):
    """노드를 실행합니다."""
    rclpy.init(args=args)
    node = RegionPenClient()
```

먼저 ROS 2를 초기화해.

```python
rclpy.init(args=args)
```

그다음 노드를 생성해.

```python
node = RegionPenClient()
```

노드가 생성되면 `__init__()`이 실행되면서 다음 작업이 이루어져.

1. 노드 초기화
2. `current_region`을 `None`으로 설정
3. `/turtle1/set_pen` 서비스 클라이언트 생성
4. `/turtle1/pose` 토픽 구독 등록

여기까지는 위치를 수신할 준비를 마친 상태야.

## 16-1. `rclpy.spin(node)`

```python
try:
    rclpy.spin(node)
```

이 코드는 노드가 계속 메시지와 이벤트를 처리하도록 해.

왜 필요할까?

`create_subscription()`으로 구독을 등록했다고 해서 콜백 함수가 그 자리에서 계속 실행되는 것은 아니야.

ROS 2가 메시지를 처리하고 콜백을 실행할 수 있도록 실행 흐름을 유지해야 해.

이번 코드에서는 다음과 같은 흐름이 반복돼.

```text
rclpy.spin(node)
      │
      ▼
/turtle1/pose 메시지 수신
      │
      ▼
on_pose(message) 실행
      │
      ▼
현재 x좌표 확인
      │
      ▼
왼쪽/오른쪽 영역 판단
      │
      ▼
영역이 바뀌었는지 확인
      │
      ▼
필요한 경우 펜 색상 변경 서비스 호출
```

따라서 `rclpy.spin(node)`은 이 프로그램이 위치 정보를 계속 받아서 처리할 수 있도록 해주는 중요한 코드야.

## 16-2. 종료 처리

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

`Ctrl + C`를 눌러 프로그램을 종료하면 `KeyboardInterrupt`가 발생할 수 있어.

`finally` 블록에서는 노드를 정리하고 ROS 2 종료를 시도해.

이렇게 하면 프로그램이 종료될 때 노드와 관련된 자원을 정리할 수 있어.

---

# 17. 전체 동작을 순서도로 이해하기

지금까지 배운 내용을 하나로 연결하면 다음과 같아.

```text
프로그램 시작
    │
    ▼
ROS 2 초기화
    │
    ▼
RegionPenClient 노드 생성
    │
    ├── /turtle1/pose 구독
    │
    └── /turtle1/set_pen 클라이언트 생성
    │
    ▼
rclpy.spin(node)
    │
    ▼
위치 메시지 수신
    │
    ▼
message.x < 5.0 ?
    │
    ├── 참 → left
    │
    └── 거짓 → right
    │
    ▼
new_region == current_region ?
    │
    ├── 참 → return
    │          │
    │          └── 서비스 호출하지 않음
    │
    └── 거짓
          │
          ▼
    current_region 갱신
          │
          ▼
    call_set_pen_service()
          │
          ├── left  → 노란색
          │
          └── right → 초록색
          │
          ▼
    /turtle1/set_pen 호출
```

이 프로그램은 거북이의 위치를 계속 확인하면서, 영역이 변경되었을 때만 색상을 바꿔.

---

# 18. Ubuntu에서 실행하는 방법

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 환경을 기준으로 설명할게.

## 터미널 1: turtlesim 실행

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

시뮬레이터 창이 나타나는지 확인해.

## 터미널 2: 패키지 빌드

새 터미널을 열고 다음을 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 완료되면 워크스페이스 환경을 불러와.

```bash
source install/setup.bash
```

그다음 실행해.

```bash
ros2 run turtle_robot lesson_10_region_pen_client
```

이 명령이 실행되려면 `turtle_robot` 패키지의 `setup.py`에 `lesson_10_region_pen_client` 실행 항목이 등록되어 있어야 해.

실행한 후 거북이를 움직이면 왼쪽과 오른쪽 영역에 따라 펜 색상이 바뀌어야 해.

---

# 19. 직접 움직여서 테스트하기

세 번째 터미널을 열어 거북이를 직접 조종해 보자.

먼저 환경을 불러와.

```bash
source /opt/ros/jazzy/setup.bash
```

그다음 키보드 조종 프로그램을 실행해.

```bash
ros2 run turtlesim turtle_teleop_key
```

키보드의 방향키를 이용해서 거북이를 움직여 봐.

- 왼쪽 영역에 진입하면 펜 색상이 노란색으로 변경돼.
- 오른쪽 영역에 진입하면 펜 색상이 초록색으로 변경돼.
- 같은 영역에서 움직이는 동안에는 색상 변경 요청을 반복해서 보내지 않아.

**주의:** 펜 색상 변경은 거북이의 펜 설정을 바꾸는 작업이야. 이미 화면에 그려진 선의 색상까지 모두 변경하는 것은 아니야. 이전에 그려진 선은 그대로 남고, 색상 변경 이후에 그리는 선부터 새로운 색상이 적용돼.

또한 `turtlesim`에서는 펜이 내려가 있는 상태에서 움직여야 선이 그려져. 기본 설정에서는 일반적으로 펜이 내려가 있어.

---

# 20. 동작을 확인하는 ROS 2 명령어

코드가 제대로 실행되는지 확인하려면 다음 명령어를 사용할 수 있어.

### ① 노드 목록 확인

```bash
ros2 node list
```

출력에서 다음 이름을 찾아봐.

```text
/lesson_10_region_pen_client
```

### ② 위치 토픽 확인

```bash
ros2 topic echo /turtle1/pose
```

거북이의 위치와 방향 정보가 계속 출력돼.

예를 들어 다음과 같은 값이 나올 수 있어.

```yaml
x: 3.0
y: 4.0
theta: 0.0
```

이때 `x`가 5.0보다 작으므로 왼쪽 영역이야.

### ③ 서비스 타입 확인

```bash
ros2 service type /turtle1/set_pen
```

정상적으로 서비스가 존재한다면 다음과 같이 출력돼.

```text
turtlesim/srv/SetPen
```

### ④ 펜 서비스 요청 필드 확인

```bash
ros2 interface show turtlesim/srv/SetPen
```

이 명령어를 사용하면 서비스 요청과 응답에 어떤 필드가 있는지 확인할 수 있어.

---

# 21. 이번 실습에서 꼭 이해해야 하는 개념 5가지

| 핵심 코드 | 배워야 하는 개념 |
|---|---|
| `create_subscription()` | 토픽 구독 |
| `self.on_pose` | 콜백 함수 |
| `message.x < 5.0` | 조건문을 이용한 영역 판단 |
| `self.current_region` | 이전 상태 저장 |
| `self.client.call_async(req)` | 비동기 서비스 호출 |

이번 실습에서 가장 중요한 것은 **토픽과 서비스를 함께 사용하는 방법**이야.

토픽은 거북이의 위치 정보를 지속적으로 전달해.

```python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.on_pose,
    10
)
```

반면 서비스는 필요할 때 펜 색상 변경을 요청하는 데 사용해.

```python
self.client.call_async(req)
```

두 가지를 연결하면 거북이의 위치에 따라 자동으로 동작하는 프로그램을 만들 수 있어.

이런 구조는 실제 로봇에서도 유용해. 예를 들어 센서에서 거리 정보를 받아 장애물과의 거리를 판단하고, 조건이 충족되었을 때 모터나 다른 장치에 동작을 요청하는 식으로 확장할 수 있어.

