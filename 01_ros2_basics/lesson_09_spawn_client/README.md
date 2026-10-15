
# 1. 이 코드는 무엇을 하는 걸까?

`turtlesim`을 실행하면 기본적으로 거북이 한 마리가 나타나.

이 거북이의 이름은 `turtle1`이야.

이번 코드를 실행하면 다음과 같이 돼.

- 기존 거북이: `turtle1`
- 새로 생성할 거북이: `turtle2`
- 생성 위치: x = 2.0, y = 2.0
- 거북이의 방향: 0.0 라디안

예를 들어, 다음과 같은 상황을 만드는 거야.

```text
┌───────────────────────────────┐
│                               │
│                               │
│                               │
│                               │
│                               │
│                               │
│  🐢 turtle2                   │
│                               │
│                               │
│                   🐢 turtle1 │
└───────────────────────────────┘
```

위 그림은 이해를 돕기 위한 예시야. 실제 거북이의 위치는 생성 요청과 기존 거북이의 위치에 따라 달라져.

핵심은 **`/spawn`이라는 서비스를 호출해 새로운 거북이를 생성한다는 것**이야.

---

# 2. 전체 코드 살펴보기

네가 작성한 코드를 기능별로 나누면 다음과 같아.

| 코드 부분 | 역할 |
|---|---|
| `import` | 필요한 ROS 2 기능을 불러옴 |
| `class SpawnClient(Node)` | 거북이 생성 요청을 담당하는 노드 |
| `__init__()` | 노드를 초기화하고 서비스 클라이언트를 생성 |
| `send_request()` | 거북이 생성 요청을 작성하고 전송 |
| `main()` | ROS 2를 초기화하고 요청이 완료될 때까지 기다림 |
| `finally` | 프로그램 종료 시 노드를 정리 |

전체적인 실행 흐름은 다음과 같아.

```text
프로그램 시작
    ↓
ROS 2 초기화
    ↓
SpawnClient 노드 생성
    ↓
/spawn 서비스가 준비될 때까지 대기
    ↓
거북이 생성 요청 작성
    ↓
/spawn 서비스로 요청 전송
    ↓
요청이 완료될 때까지 대기
    ↓
응답 확인
    ↓
노드 종료 및 자원 정리
```

이제 각각 자세히 알아보자.

# 3. 필요한 기능 불러오기

```python
"""두 번째 거북이를 만드는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn  # noqa: F401
```

## 3-1. 문서 문자열

```python
"""두 번째 거북이를 만드는 서비스 실습입니다."""
```

이 문장은 프로그램의 목적을 설명해.

Python에서는 함수나 클래스, 모듈의 첫 부분에 큰따옴표 세 개로 설명을 작성할 수 있어.

이를 **독스트링(docstring)**이라고 해.

예를 들어 다음과 같이 작성할 수도 있어.

```python
"""로봇의 위치를 확인하는 프로그램입니다."""
```

프로그램 실행에 직접적인 영향을 주는 코드는 아니지만, 코드의 목적을 이해하는 데 도움이 돼.

## 3-2. ROS 2 기능 불러오기

```python
import rclpy
```

`rclpy`는 Python에서 ROS 2를 사용할 수 있게 해주는 라이브러리야.

ROS 2 노드를 초기화하거나, 메시지를 처리하거나, 프로그램을 종료할 때 사용해.

대표적인 기능은 다음과 같아.

```python
rclpy.init()
rclpy.spin(node)
rclpy.shutdown()
```

각각의 역할은 다음과 같아.

| 명령 | 역할 |
|---|---|
| `rclpy.init()` | ROS 2 초기화 |
| `rclpy.spin(node)` | 노드의 콜백 등을 계속 처리 |
| `rclpy.shutdown()` | ROS 2 종료 |

네 코드에서는 `rclpy.init()`과 `rclpy.try_shutdown()`을 사용하고 있어.

## 3-3. Node 불러오기

```python
from rclpy.node import Node
```

`Node`는 ROS 2에서 노드를 만들기 위한 클래스야.

노드는 로봇 시스템을 구성하는 독립적인 실행 단위라고 생각하면 돼.

예를 들어 로봇 시스템에서는 다음과 같은 노드를 만들 수 있어.

```text
ROS 2 시스템
    │
    ├── 카메라 노드
    ├── 거리 센서 노드
    ├── 모터 제어 노드
    └── 거북이 생성 노드
```

이번 실습에서는 거북이 생성 요청을 담당하는 노드를 만들 거야.

## 3-4. Spawn 불러오기

```python
from turtlesim.srv import Spawn  # noqa: F401
```

여기서 가장 중요한 것은 `Spawn`이야.

`Spawn`은 `turtlesim`에서 새로운 거북이를 생성할 때 사용하는 **서비스 타입**이야.

서비스 타입에는 요청(Request)과 응답(Response)의 구조가 정의되어 있어.

`Spawn` 서비스의 요청에는 다음 정보가 포함돼.

| 필드 | 자료형 | 의미 |
|---|---|---|
| `x` | `float32` | 생성할 위치의 x좌표 |
| `y` | `float32` | 생성할 위치의 y좌표 |
| `theta` | `float32` | 거북이의 방향 |
| `name` | `string` | 생성할 거북이의 이름 |

서비스가 성공적으로 처리되면 응답에는 생성된 거북이의 이름이 들어 있어.

여기서 `# noqa: F401`은 코드 검사 도구에 전달하는 주석이야. 일반적으로 사용되지 않는 import를 경고하지 않도록 하는 용도야.

---

# 4. SpawnClient 클래스 만들기

```python
class SpawnClient(Node):
    """새 거북이 생성을 요청하는 노드입니다."""
```

이 코드는 `SpawnClient`라는 클래스를 정의해.

여기서 다음 부분을 보자.

```python
class SpawnClient(Node):
```

`SpawnClient`가 `Node`를 상속한다는 뜻이야.

쉽게 말하면 ROS 2 노드가 갖고 있는 기능을 물려받아, 거북이를 생성하는 데 필요한 기능을 추가하는 거야.

클래스의 이름은 직접 정할 수 있어.

예를 들어 다음과 같이 작성해도 돼.

```python
class RobotController(Node):
    pass
```

다만 이번 실습에서는 거북이 생성 요청을 담당하므로 `SpawnClient`라는 이름을 사용한 거야.

## 4-1. `__init__()` 이해하기

```python
def __init__(self):
    super().__init__('lesson_09_spawn_client')
```

`__init__()`은 Python에서 객체를 생성할 때 실행되는 특별한 메서드야.

이 부분이 실행되면 노드가 초기화돼.

### `self`는 무엇일까?

```python
def __init__(self):
```

`self`는 현재 객체 자신을 가리켜.

예를 들어 다음과 같은 코드가 있다고 생각해 보자.

```python
self.speed = 1.0
```

현재 객체에 `speed`라는 값을 저장하는 거야.

나중에 같은 객체 안의 다른 메서드에서 다음과 같이 사용할 수 있어.

```python
print(self.speed)
```

ROS 2 코드에서도 똑같은 원리로 사용해.

### `super().__init__()`은 무엇일까?

```python
super().__init__('lesson_09_spawn_client')
```

부모 클래스인 `Node`의 초기화 기능을 호출하는 코드야.

여기서 전달한 문자열은 노드의 이름이야.

따라서 노드 이름은 다음과 같아.

```text
lesson_09_spawn_client
```

터미널에서 확인하려면 다음 명령을 실행해.

```bash
ros2 node list
```

프로그램이 실행 중이면 출력에 다음 이름이 나타날 수 있어.

```text
/lesson_09_spawn_client
```

단, 노드는 프로그램이 실행되는 동안에만 목록에 나타나.

---

# 5. 서비스 클라이언트 생성하기

이 부분은 이번 실습의 핵심 중 하나야.

```python
self.client = self.create_client(Spawn, '/spawn')
```

한 부분씩 살펴보자.

### `self.create_client()`

ROS 2 노드에서 서비스를 호출할 수 있는 클라이언트를 생성하는 메서드야.

여기서는 다음과 같이 사용했어.

```python
self.create_client(서비스_타입, 서비스_이름)
```

실제 코드에서는 다음과 같지.

```python
self.create_client(Spawn, '/spawn')
```

각 인수의 의미는 다음과 같아.

| 인수 | 의미 |
|---|---|
| `Spawn` | 서비스 요청과 응답의 형식 |
| `'/spawn'` | 호출할 서비스의 이름 |

### `/spawn`은 무엇일까?

`/spawn`은 `turtlesim` 노드가 제공하는 서비스 이름이야.

이 서비스를 호출하면 새로운 거북이를 생성할 수 있어.

서비스의 구조를 간단하게 표현하면 다음과 같아.

```text
SpawnClient 노드
       │
       │ 거북이 생성 요청
       ▼
    /spawn 서비스
       │
       ▼
turtlesim 노드
       │
       │ 새 거북이 생성
       ▼
  생성 결과 응답
```

여기서 기억해야 할 점이 있어.

**서비스 클라이언트를 생성했다고 해서 거북이가 바로 생성되는 것은 아니야.**

서비스를 호출할 수 있는 준비를 마친 것뿐이야.

실제로 거북이를 생성하려면 요청을 작성하고 전송해야 해.

---

# 6. `send_request()` 메서드 이해하기

```python
def send_request(self):
    self.client.wait_for_service()
    """거북이 생성 요청을 보냅니다."""
```

이 메서드는 거북이를 생성하기 위한 요청을 준비하고 서비스에 전달하는 역할을 해.

## 6-1. 서비스가 준비될 때까지 기다리기

```python
self.client.wait_for_service()
```

이 코드는 `/spawn` 서비스가 사용 가능해질 때까지 기다려.

예를 들어 다음과 같은 상황을 생각해 보자.

1. 거북이 생성 프로그램을 실행했어.
2. 그런데 `turtlesim`은 아직 실행하지 않았어.
3. `/spawn` 서비스를 제공하는 노드가 없어.
4. 클라이언트는 서비스를 사용할 수 있을 때까지 기다려.

`turtlesim`이 실행되어 `/spawn` 서비스가 준비되면 다음 단계로 넘어갈 수 있어.

이 메서드는 기본적으로 서비스가 나타날 때까지 기다리며, 인수를 지정해 제한 시간을 설정할 수도 있어.

예를 들면 다음과 같아.

```python
self.client.wait_for_service(timeout_sec=5.0)
```

이렇게 하면 최대 5초 동안 기다려.

다만 이 코드는 반환값을 확인해야 해. 5초 안에 서비스가 준비되지 않으면 `False`가 반환될 수 있어.

### 참고: 독스트링의 위치

현재 코드에서는 다음과 같이 작성했어.

```python
def send_request(self):
    self.client.wait_for_service()
    """거북이 생성 요청을 보냅니다."""
```

Python에서 메서드의 독스트링은 **메서드 본문의 첫 번째 문장**이어야 해.

따라서 다음과 같이 작성하는 것이 좋아.

```python
def send_request(self):
    """거북이 생성 요청을 보냅니다."""
    self.client.wait_for_service()
```

이렇게 하면 문서 문자열로 정상 인식돼.

---

# 7. Spawn 요청 메시지 만들기

이제 실제로 거북이 생성에 필요한 정보를 작성하는 부분이야.

```python
request = Spawn.Request()
request.x = 2.0
request.y = 2.0
request.theta = 0.0
request.name = 'turtle2'
```

## 7-1. 요청 객체 만들기

```python
request = Spawn.Request()
```

`Spawn.Request()`는 `Spawn` 서비스의 요청 형식에 맞는 객체를 생성해.

쉽게 말하면 **거북이 생성 신청서**를 만드는 거야.

신청서에는 거북이의 위치, 방향, 이름을 적을 수 있어.

## 7-2. x좌표 지정하기

```python
request.x = 2.0
```

새로운 거북이의 x좌표를 `2.0`으로 지정해.

`turtlesim`의 좌표는 시뮬레이터 화면 안에서 사용되는 좌표야.

x좌표는 화면의 좌우 방향을 나타내.

- x값이 작아지면 왼쪽으로 이동
- x값이 커지면 오른쪽으로 이동

따라서 `x = 2.0`은 화면 왼쪽에 가까운 위치를 의미해.

## 7-3. y좌표 지정하기

```python
request.y = 2.0
```

새로운 거북이의 y좌표를 `2.0`으로 지정해.

y좌표는 화면의 위아래 방향을 나타내.

- y값이 작아지면 아래쪽
- y값이 커지면 위쪽

따라서 x와 y를 모두 2.0으로 지정하면 화면의 왼쪽 아래쪽에 가까운 위치에 생성돼.

`turtlesim` 화면의 일반적인 좌표 범위는 약 0부터 11까지야.

정확한 위치는 화면 크기와 좌표계에 따라 이해하면 돼.

## 7-4. 방향 지정하기

```python
request.theta = 0.0
```

거북이가 바라볼 방향을 지정해.

여기서 `theta`는 각도를 나타내며, 단위는 **도(degree)가 아니라 라디안(radian)**이야.

주요 값은 다음과 같아.

| `theta` | 방향 |
|---:|---|
| `0.0` | 오른쪽 |
| `1.5708` | 위쪽 |
| `3.14159` | 왼쪽 |
| `4.71239` | 아래쪽 |

이 값들은 각각 약 0°, 90°, 180°, 270°에 해당해.

따라서 현재 코드의

```python
request.theta = 0.0
```

은 거북이가 오른쪽을 바라보도록 지정하는 거야.

## 7-5. 거북이 이름 지정하기

```python
request.name = 'turtle2'
```

생성할 거북이의 이름을 지정해.

이번 실습에서는 이름을 `turtle2`로 정했어.

이 이름은 이후에 토픽이나 서비스 이름을 사용할 때도 중요해.

예를 들어 거북이가 생성되면 다음과 같은 토픽이 생길 수 있어.

```text
/turtle2/cmd_vel
/turtle2/pose
/turtle2/color_sensor
```

각 토픽은 다음과 같은 역할을 해.

| 토픽 | 역할 |
|---|---|
| `/turtle2/cmd_vel` | 두 번째 거북이의 속도 명령 |
| `/turtle2/pose` | 두 번째 거북이의 위치와 방향 |
| `/turtle2/color_sensor` | 두 번째 거북이 아래의 색상 정보 |

이름을 `turtle2`로 지정하면 이후 해당 거북이를 제어할 때도 이 이름을 사용하면 돼.

**주의:** 이미 `turtle2`라는 이름의 거북이가 존재하면 같은 이름으로 다시 생성할 수 없어. 중복된 이름으로 요청하면 서비스에서 오류가 발생할 수 있어.

---

# 8. 서비스 요청 전송하기

```python
return self.client.call_async(request)
```

이 부분도 매우 중요해.

앞에서 만든 `request` 객체를 `/spawn` 서비스에 전달하는 코드야.

## 8-1. `call_async()`란?

`call_async()`는 서비스를 비동기 방식으로 호출해.

```python
self.client.call_async(request)
```

여기서 `async`는 비동기(asynchronous)를 의미해.

쉽게 설명하면 다음과 같아.

**서비스에 요청을 보내고, 결과를 기다리는 동안에도 프로그램이 다른 작업을 처리할 수 있도록 하는 방식**이야.

비동기 호출의 결과를 추적하기 위해 `Future` 객체가 반환돼.

현재 코드는 다음과 같아.

```python
return self.client.call_async(request)
```

이렇게 하면 반환된 `Future` 객체를 호출한 쪽에서 사용할 수 있어.

`Future`는 요청의 완료 여부와 결과를 확인할 때 사용하는 객체라고 생각하면 돼.

예를 들어 다음과 같이 사용할 수 있어.

```python
future = node.send_request()
```

여기서 `future`에는 서비스 요청의 처리 결과를 추적하는 객체가 들어가.

---

# 9. `main()` 함수 자세히 알아보기

이제 전체 프로그램을 실행하는 부분이야.

```python
def main(args=None):
    """서비스를 호출합니다."""
    rclpy.init(args=args)
    node = SpawnClient()
```

## 9-1. `main()` 함수

```python
def main(args=None):
```

프로그램이 시작될 때 실행할 작업을 정의하는 함수야.

ROS 2 Python 패키지에서는 이런 형태로 실행 함수를 작성하는 경우가 많아.

## 9-2. ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2를 초기화하는 코드야.

노드를 생성하고 ROS 2 기능을 사용하기 전에 초기화해야 해.

## 9-3. 노드 생성

```python
node = SpawnClient()
```

앞에서 만든 `SpawnClient` 클래스를 실제 객체로 만드는 부분이야.

이때 클래스의 `__init__()`이 실행되므로 다음 작업이 이루어져.

1. `lesson_09_spawn_client`라는 이름으로 노드를 초기화해.
2. `/spawn` 서비스의 클라이언트를 생성해.

이 시점에서는 아직 서비스 요청을 보내지 않았으므로 거북이가 생성되지 않았을 수 있어.

---

# 10. 서비스 호출과 결과 확인

```python
try:
    future = node.send_request()
    rclpy.spin_until_future_complete(node, future)
    response = future.result()
```

여기가 실제 서비스 요청을 처리하는 부분이야.

## 10-1. 서비스 요청 보내기

```python
future = node.send_request()
```

`send_request()`를 호출하면 다음 작업이 진행돼.

1. `/spawn` 서비스가 준비될 때까지 기다려.
2. 요청 객체를 만들어.
3. x, y, theta, name을 지정해.
4. `call_async()`로 요청을 전송해.
5. `Future` 객체를 반환해.

반환된 객체를 `future` 변수에 저장하는 거야.

## 10-2. 요청이 완료될 때까지 기다리기

```python
rclpy.spin_until_future_complete(node, future)
```

이 함수는 지정한 `Future`가 완료될 때까지 노드의 처리를 진행해.

여기서 `future`는 앞에서 호출한 서비스 요청의 진행 상태를 나타내.

예를 들어 다음과 같은 상황이 있다고 생각해 보자.

```text
요청 전송
   ↓
서비스가 요청 처리
   ↓
새로운 거북이 생성
   ↓
서비스 응답 반환
   ↓
Future 완료
```

`spin_until_future_complete()`는 요청이 완료될 때까지 기다린 다음 반환해.

이 코드에서는 서비스 요청의 결과를 확인하기 전에 완료될 때까지 기다리는 거야.

## 10-3. 서비스 응답 가져오기

```python
response = future.result()
```

요청이 완료되면 `future.result()`로 결과를 가져올 수 있어.

`Spawn` 서비스의 응답에는 생성된 거북이의 이름이 포함돼.

예를 들어 성공적으로 생성되었다면 응답의 이름은 다음과 같을 수 있어.

```python
response.name
```

출력하려면 다음 코드를 사용할 수 있어.

```python
print(response.name)
```

성공적으로 생성되었다면 다음과 같은 결과가 나올 거야.

```text
turtle2
```

여기서 중요한 점은 **`future.result()`를 호출했다고 해서 무조건 성공한 것은 아니라는 것**이야.

서비스 처리 과정에서 예외가 발생할 수도 있고, 중복 이름처럼 요청 자체가 거부될 수도 있어.

따라서 실제 프로그램에서는 예외 처리도 고려하는 것이 좋아.

---

# 11. 예외 처리와 프로그램 종료

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

## 11-1. `KeyboardInterrupt`

```python
except KeyboardInterrupt:
    pass
```

프로그램 실행 중 사용자가 `Ctrl + C`를 눌렀을 때 발생할 수 있는 예외를 처리해.

`pass`는 아무 작업도 하지 않고 넘어가라는 의미야.

즉, 사용자가 실행을 중단했을 때 해당 예외가 발생해도 프로그램이 종료 정리 과정으로 넘어갈 수 있게 해.

## 11-2. `finally`

```python
finally:
```

`finally` 블록은 예외 발생 여부와 관계없이 실행되는 정리 작업을 작성하는 데 사용해.

여기서는 노드와 ROS 2를 정리해.

## 11-3. 노드 종료

```python
node.destroy_node()
```

생성한 ROS 2 노드를 정리해.

## 11-4. ROS 2 종료

```python
rclpy.try_shutdown()
```

ROS 2가 아직 종료되지 않았다면 종료를 시도해.

이미 종료된 상태일 때도 안전하게 종료 처리를 할 수 있도록 사용하는 함수야.

---

# 12. 코드에서 개선하면 좋은 점

네 코드의 핵심 구조는 맞아. 다만 몇 가지를 개선하면 서비스 호출 결과를 더 쉽게 확인할 수 있어.

특히 다음 세 가지를 추천해.

1. 독스트링을 메서드의 첫 줄로 이동하기
2. 서비스 응답에 포함된 거북이 이름 출력하기
3. 서비스 호출 결과를 확인하고 오류를 처리하기

다음은 개선한 전체 코드야.

```python
"""두 번째 거북이를 만드는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn


class SpawnClient(Node):
    """새 거북이 생성을 요청하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_09_spawn_client')

        # /spawn 서비스의 클라이언트를 생성합니다.
        self.client = self.create_client(Spawn, '/spawn')

    def send_request(self):
        """거북이 생성 요청을 보냅니다."""

        # 서비스가 준비될 때까지 기다립니다.
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('/spawn 서비스를 기다리는 중입니다...')

        # 거북이 생성 요청을 작성합니다.
        request = Spawn.Request()
        request.x = 2.0
        request.y = 2.0
        request.theta = 0.0
        request.name = 'turtle2'

        # 요청을 비동기로 전송하고 Future를 반환합니다.
        return self.client.call_async(request)


def main(args=None):
    """서비스를 호출합니다."""

    rclpy.init(args=args)
    node = SpawnClient()

    try:
        future = node.send_request()

        # 서비스 요청이 완료될 때까지 기다립니다.
        rclpy.spin_until_future_complete(node, future)

        # 서비스 응답을 확인합니다.
        if future.done():
            response = future.result()

            if response is not None:
                node.get_logger().info(
                    f'생성된 거북이 이름: {response.name}'
                )
            else:
                node.get_logger().error('서비스 응답이 없습니다.')

    except KeyboardInterrupt:
        pass

    except Exception as e:
        node.get_logger().error(f'서비스 호출 중 오류 발생: {e}')

    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

이 코드에서는 서비스가 준비되지 않았을 때 1초마다 상태를 확인하고, 준비될 때까지 대기해.

다만 이 코드도 서비스가 영원히 준비되지 않으면 계속 기다릴 수 있어. 무한 대기를 피하고 싶다면 최대 대기 시간을 별도로 설정하면 돼.

또한 `response is not None`이라는 검사만으로 모든 서비스 오류를 처리할 수 있는 것은 아니야. 서비스 호출에서 예외가 발생하는 경우도 고려해야 해.

---

# 13. Ubuntu에서 실행하는 방법

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 환경을 기준으로 설명할게.

## 터미널 1: turtlesim 실행

먼저 터미널을 열고 다음 명령어를 입력해.

```bash
source /opt/ros/jazzy/setup.bash
```

그다음:

```bash
ros2 run turtlesim turtlesim_node
```

거북이 한 마리가 보이는 시뮬레이터 창이 나타나면 정상적으로 실행된 거야.

이 터미널은 계속 켜 두면 돼.

## 터미널 2: 워크스페이스 빌드

새 터미널을 열어.

```bash
source /opt/ros/jazzy/setup.bash
```

워크스페이스로 이동해.

```bash
cd ~/ros2_ws
```

패키지를 빌드해.

```bash
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 다음 명령어를 실행해.

```bash
source install/setup.bash
```

그다음 프로그램을 실행해.

```bash
ros2 run turtle_robot lesson_09_spawn_client
```

**참고:** 이 명령어가 동작하려면 `turtle_robot` 패키지의 `setup.py`에 `lesson_09_spawn_client` 실행 항목이 등록되어 있어야 해.

## 정상 실행 결과

성공적으로 실행되면 터미널에 다음과 비슷한 로그가 나타날 수 있어.

```text
[INFO] [lesson_09_spawn_client]: 생성된 거북이 이름: turtle2
```

그리고 `turtlesim` 창에 두 번째 거북이가 나타나야 해.

---

# 14. 서비스가 실제로 생성됐는지 확인하기

거북이가 생성된 뒤에는 ROS 2 명령어로 확인할 수 있어.

### ① 서비스 목록 확인

```bash
ros2 service list
```

출력에 다음 항목이 있는지 확인해.

```text
/spawn
```

### ② 서비스 타입 확인

```bash
ros2 service type /spawn
```

정상적인 경우 다음과 같이 나와.

```text
turtlesim/srv/Spawn
```

### ③ 두 번째 거북이의 토픽 확인

```bash
ros2 topic list
```

거북이가 정상적으로 생성됐다면 다음과 같은 토픽이 나타날 수 있어.

```text
/turtle2/cmd_vel
/turtle2/pose
/turtle2/color_sensor
```

### ④ 두 번째 거북이의 위치 확인

```bash
ros2 topic echo /turtle2/pose
```

이 명령어를 실행하면 두 번째 거북이의 위치와 방향 정보가 출력돼.

예를 들어 다음과 같은 데이터가 나올 수 있어.

```yaml
x: 2.0
y: 2.0
theta: 0.0
```

실제 출력값은 거북이가 이동했는지에 따라 달라질 수 있어.

종료하려면 `Ctrl + C`를 누르면 돼.

---

# 15. 이번 실습에서 꼭 기억할 핵심

지금까지 배운 서비스 실습을 비교하면 이해하기 쉬워.

| 실습 | 서비스 | 기능 |
|---|---|---|
| `lesson_08_teleport_client` | `/turtle1/teleport_absolute` | 기존 거북이를 순간이동 |
| `lesson_09_spawn_client` | `/spawn` | 새로운 거북이 생성 |

이번 코드에서 반드시 이해해야 할 부분은 다음 네 가지야.

**첫째, 클라이언트 생성**

```python
self.client = self.create_client(Spawn, '/spawn')
```

서비스를 호출할 수 있는 클라이언트를 만들어.

**둘째, 요청 메시지 작성**

```python
request = Spawn.Request()
request.x = 2.0
request.y = 2.0
request.theta = 0.0
request.name = 'turtle2'
```

생성할 거북이의 위치, 방향, 이름을 지정해.

**셋째, 서비스 요청 전송**

```python
return self.client.call_async(request)
```

요청을 전송하고 `Future` 객체를 반환해.

**넷째, 결과 확인**

```python
rclpy.spin_until_future_complete(node, future)
response = future.result()
```

요청이 완료될 때까지 기다린 뒤 서비스 응답을 가져와.

이 네 가지 구조는 앞으로 ROS 2에서 서비스 클라이언트를 작성할 때 반복해서 사용하게 될 거야.
