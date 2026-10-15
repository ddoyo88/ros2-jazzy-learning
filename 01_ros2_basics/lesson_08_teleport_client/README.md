
# 1. 전체 프로그램의 동작 원리

먼저 프로그램이 어떻게 작동하는지 살펴보자.

이번 실습의 목표는 거북이를 다음 위치로 순간이동시키는 거야.

```text
x = 2.0
y = 2.0
theta = 0.0
```

여기서 `x`, `y`는 위치이고 `theta`는 거북이가 바라볼 방향이야.

전체 통신 구조는 다음과 같아.

```text
┌─────────────────────────────┐
│ TeleportClient              │
│                             │
│ 거북이 순간이동 요청 준비    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Service Client              │
│                             │
│ /turtle1/teleport_absolute  │
└──────────────┬──────────────┘
               │
               │ 요청 전송
               ▼
┌─────────────────────────────┐
│ turtlesim                   │
│                             │
│ 순간이동 서비스 처리        │
└──────────────┬──────────────┘
               │
               │ 응답 반환
               ▼
┌─────────────────────────────┐
│ TeleportClient              │
│                             │
│ 요청 완료 확인              │
└─────────────────────────────┘
```

Publisher와 다른 점은 무엇일까?

Publisher는 메시지를 발행하고, Subscriber는 메시지를 수신해.

반면 Service는 **요청(Request)을 보내고, 처리 결과에 대한 응답(Response)을 받는 통신 방식**이야.

예를 들어 다음과 같은 상황에서 사용할 수 있어.

- 거북이를 특정 위치로 이동하기
- 새로운 거북이 생성하기
- 시뮬레이션 초기화하기
- 로봇의 특정 기능 실행 요청하기

이번에는 순간이동 서비스를 호출하는 거야.

---

# 2. 라이브러리 가져오기

먼저 코드의 맨 위를 살펴보자.

```python
import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute  # noqa: F401
```

각 줄의 역할은 다음과 같아.

| 코드 | 역할 |
|---|---|
| `import rclpy` | ROS 2 Python 기능 사용 |
| `from rclpy.node import Node` | ROS 2 노드 생성 |
| `TeleportAbsolute` | 순간이동 서비스의 요청 및 응답 타입 사용 |

## 2-1. `rclpy`

```python
import rclpy
```

ROS 2에서 Python 프로그램을 작성하기 위한 라이브러리야.

이번 실습에서는 다음 기능을 사용해.

```python
rclpy.init()
```

ROS 2 초기화

```python
rclpy.spin_until_future_complete(node, future)
```

서비스 요청의 처리가 완료될 때까지 노드를 실행하며 기다리는 기능

```python
rclpy.try_shutdown()
```

ROS 2 종료 처리

## 2-2. `Node`

```python
from rclpy.node import Node
```

ROS 2 노드를 만들기 위한 기본 클래스야.

이번에는 `TeleportClient`라는 노드를 만들 거야.

이 노드는 거북이에게 순간이동을 요청하는 역할을 담당해.

## 2-3. `TeleportAbsolute`

```python
from turtlesim.srv import TeleportAbsolute
```

이 부분이 이번 실습에서 가장 중요해.

`TeleportAbsolute`는 turtlesim에서 제공하는 순간이동 서비스 타입이야.

이 서비스를 이용하면 거북이를 원하는 좌표와 방향으로 순간이동시킬 수 있어.

서비스 타입은 다음 명령어로 확인할 수도 있어.

```bash
ros2 service type /turtle1/teleport_absolute
```

정상적으로 서비스가 실행 중이라면 다음과 같은 결과가 나와.

```text
turtlesim/srv/TeleportAbsolute
```

서비스의 요청과 응답 구조를 자세히 보려면 다음 명령어를 사용해.

```bash
ros2 interface show turtlesim/srv/TeleportAbsolute
```

그러면 요청에 필요한 필드와 응답의 구조를 확인할 수 있어.

---

# 3. TeleportClient 클래스

```python
class TeleportClient(Node):
    """순간이동 서비스를 요청하는 노드입니다."""
```

이 코드는 `TeleportClient`라는 클래스를 정의해.

여기서 중요한 부분은 괄호 안의 `Node`야.

```python
class TeleportClient(Node):
```

이것은 `TeleportClient`가 ROS 2의 `Node` 클래스를 상속받는다는 의미야.

따라서 ROS 2에서 제공하는 기능을 사용할 수 있어.

예를 들어 다음과 같은 기능이 있어.

```python
self.create_client()
```

서비스를 호출하기 위한 Client 생성

```python
self.get_logger()
```

로그 출력

이번 실습에서는 서비스를 호출하기 위해 `create_client()`를 사용할 거야.

---

# 4. `__init__()` 함수: 서비스 Client 생성

다음 코드를 살펴보자.

```python
def __init__(self):
    super().__init__('lesson_08_teleport_client')

    # 실습 1: /turtle1/teleport_absolute의 Client를 만드세요.
    self.client = self.create_client(
        TeleportAbsolute,
        '/turtle1/teleport_absolute'
    )
```

이 부분에서는 두 가지 작업을 해.

1. ROS 2 노드 이름 설정
2. 순간이동 서비스 Client 생성

## 4-1. 노드 이름 설정

```python
super().__init__('lesson_08_teleport_client')
```

부모 클래스인 `Node`의 초기화 기능을 실행하는 코드야.

노드 이름은 다음과 같아.

```text
lesson_08_teleport_client
```

실행 중인 노드는 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

출력 결과는 실행 중인 다른 노드에 따라 달라지지만, 다음과 비슷하게 나올 수 있어.

```text
/lesson_08_teleport_client
/turtlesim
```

## 4-2. Client 생성

```python
self.client = self.create_client(
    TeleportAbsolute,
    '/turtle1/teleport_absolute'
)
```

이 코드를 세 부분으로 나눠 보자.

### 첫 번째: `self.create_client()`

```python
self.create_client(...)
```

ROS 2 서비스를 호출할 수 있는 Client 객체를 생성하는 함수야.

여기서 주의할 점이 있어.

**Client를 생성했다고 해서 서비스가 즉시 실행되는 것은 아니야.**

Client를 생성하는 것은 서비스에 요청을 보낼 준비를 하는 단계야.

실제 요청은 나중에 `call_async()`를 실행할 때 전송돼.

### 두 번째: `TeleportAbsolute`

```python
TeleportAbsolute
```

어떤 종류의 서비스를 호출할지 지정해.

이번에는 거북이 순간이동 서비스이므로 `TeleportAbsolute`를 사용해.

다른 서비스라면 다른 서비스 타입을 사용해야 해.

예를 들어 거북이를 새로 생성하는 서비스에는 다음 타입을 사용해.

```python
from turtlesim.srv import Spawn
```

따라서 서비스 Client를 만들 때는 서비스 타입이 실제 서비스와 일치해야 해.

### 세 번째: 서비스 이름

```python
'/turtle1/teleport_absolute'
```

호출할 서비스의 이름이야.

ROS 2에서 서비스 이름은 서비스를 제공하는 서버와 연결하는 데 사용돼.

이번 서비스의 역할은 다음과 같아.

```text
서비스 이름:
/turtle1/teleport_absolute

서비스 타입:
turtlesim/srv/TeleportAbsolute

기능:
거북이를 지정된 위치와 방향으로 순간이동
```

이 서비스는 일반적으로 turtlesim 노드가 제공해.

통신 구조를 정리하면 다음과 같아.

```text
lesson_08_teleport_client
             │
             │ Service Client
             ▼
/turtle1/teleport_absolute
             │
             ▼
         turtlesim
             │
             ▼
        거북이 이동
```

---

# 5. `send_request()` 함수

이제 실제로 서비스 요청을 보내는 함수를 살펴보자.

```python
def send_request(self):
    self.client.wait_for_service()

    """순간이동 요청을 보냅니다."""

    request = TeleportAbsolute.Request()
    request.x = 2.0
    request.y = 2.0
    request.theta = 0.0

    return self.client.call_async(request)
```

이 함수에서는 다음 작업을 수행해.

1. 서비스가 준비될 때까지 기다리기
2. 요청 메시지 생성하기
3. 이동할 위치와 방향 지정하기
4. 서비스 요청 보내기
5. Future 반환하기

하나씩 자세히 알아보자.

## 5-1. `wait_for_service()`

```python
self.client.wait_for_service()
```

이 코드는 서비스를 사용할 수 있을 때까지 기다리는 기능이야.

예를 들어 순간이동 Client가 실행됐지만 turtlesim이 아직 실행되지 않았다면 어떻게 될까?

서비스 서버가 준비되지 않았으므로 요청을 처리할 수 없어.

따라서 서비스가 준비될 때까지 기다리는 거야.

```text
Client 실행
    │
    ▼
서비스 서버 확인
    │
    ├── 준비되지 않음 → 계속 대기
    │
    └── 준비됨 → 다음 코드 실행
```

기본적으로 서비스가 준비될 때까지 기다리는 방식이야.

필요하다면 대기 시간을 제한할 수도 있어.

```python
self.client.wait_for_service(timeout_sec=5.0)
```

이렇게 하면 최대 5초 동안 서비스가 준비되는지 기다려.

정해진 시간 안에 준비되지 않으면 `False`를 반환하므로, 반환값을 확인해서 예외 상황을 처리할 수도 있어.

예를 들어 다음과 같이 작성할 수 있어.

```python
if not self.client.wait_for_service(timeout_sec=5.0):
    self.get_logger().error('순간이동 서비스를 찾을 수 없습니다.')
    return None
```

다만 이 코드는 `send_request()`가 `None`을 반환할 수 있으므로, 호출하는 쪽에서도 그 상황을 처리해야 해.

현재 실습 코드에서는 기본 방식으로 서비스가 준비될 때까지 기다리고 있어.

### 참고: Docstring의 위치

현재 코드에서는 다음과 같이 작성했어.

```python
def send_request(self):
    self.client.wait_for_service()
    """순간이동 요청을 보냅니다."""
```

Python에서 함수 설명 문자열인 Docstring은 일반적으로 함수의 첫 번째 문장으로 작성해야 해.

따라서 다음과 같이 수정하는 것이 좋아.

```python
def send_request(self):
    """순간이동 요청을 보냅니다."""
    self.client.wait_for_service()
```

기능 자체에는 큰 차이가 없지만, 첫 번째 방식에서는 해당 문자열이 함수의 정식 Docstring으로 인식되지 않아.

---

# 6. 요청 메시지 생성하기

다음 코드를 보자.

```python
request = TeleportAbsolute.Request()
```

이 코드는 순간이동 서비스에 전달할 요청 메시지를 생성하는 코드야.

ROS 2의 Service는 크게 두 가지 데이터 구조를 가지고 있어.

- Request: 서버에 전달하는 요청
- Response: 서버가 요청을 처리한 뒤 반환하는 응답

이번에는 Request를 먼저 만들어야 해.

## 6-1. 왜 `TeleportAbsolute.Request()`일까?

```python
TeleportAbsolute.Request()
```

`TeleportAbsolute`는 서비스 타입이야.

그 안의 `Request()`를 사용하면 해당 서비스에 맞는 요청 객체를 생성할 수 있어.

쉽게 말하면 서비스 서버에 전달할 입력 양식을 만드는 거야.

이번 서비스는 다음 정보를 필요로 해.

```text
x
y
theta
```

이 값들을 요청 메시지에 담아서 서버에 전달하는 거야.

## 6-2. x 좌표 지정

```python
request.x = 2.0
```

거북이를 x 좌표 2.0으로 이동하도록 요청하는 거야.

turtlesim의 좌표는 시뮬레이터 화면의 좌표계를 사용해.

일반적으로 x 값이 커질수록 화면의 오른쪽 방향으로 이동해.

## 6-3. y 좌표 지정

```python
request.y = 2.0
```

거북이를 y 좌표 2.0으로 이동하도록 요청해.

일반적으로 y 값이 커질수록 화면의 위쪽 방향으로 이동해.

따라서 다음과 같은 요청이 만들어져.

```python
request.x = 2.0
request.y = 2.0
```

즉, 거북이를 좌표 `(2.0, 2.0)`으로 순간이동시키는 거야.

## 6-4. 방향 지정

```python
request.theta = 0.0
```

이 값은 순간이동한 뒤 거북이가 바라볼 방향을 지정해.

turtlesim에서는 `theta`를 라디안 단위로 사용해.

| `theta` 값 | 방향 |
|---:|---|
| `0.0` | 오른쪽 |
| `1.5708` | 위쪽 |
| `3.14159` | 왼쪽 |
| `-1.5708` | 아래쪽 |

따라서 다음 요청은 거북이를 `(2.0, 2.0)`으로 이동시키고 오른쪽을 향하게 해.

```python
request.x = 2.0
request.y = 2.0
request.theta = 0.0
```

여기서 중요한 점은 `theta`가 회전 속도가 아니라 **최종 방향 각도**라는 사실이야.

이전 실습의 `Twist`에서는 다음과 같이 회전 속도를 설정했지.

```python
msg.angular.z = 1.5
```

이 값은 회전 속도야.

반면 이번 서비스에서는 다음과 같이 작성해.

```python
request.theta = 0.0
```

이 값은 순간이동 후의 방향이야.

둘의 차이를 꼭 기억해 둬.

| 구분 | 코드 | 의미 |
|---|---|---|
| 회전 속도 | `msg.angular.z = 1.5` | 일정한 속도로 회전 |
| 방향 각도 | `request.theta = 0.0` | 지정한 방향을 향함 |

---

# 7. `call_async()`와 Future 이해하기

이제 서비스 요청을 보내는 핵심 코드를 보자.

```python
return self.client.call_async(request)
```

이 한 줄에는 중요한 개념이 두 가지 있어.

1. `call_async()`
2. `Future`

먼저 `call_async()`부터 알아보자.

## 7-1. `call_async(request)`

```python
self.client.call_async(request)
```

이 코드는 요청 메시지를 서비스 서버로 보내는 기능이야.

여기서 `async`는 비동기 방식이라는 뜻이야.

쉽게 설명하면 다음과 같아.

**요청을 보낸 뒤 응답이 도착할 때까지 그 함수 호출이 계속 붙잡혀 있지 않는 방식**이야.

예를 들어 다음 코드가 있다고 해 보자.

```python
future = self.client.call_async(request)
```

이 코드를 실행하면 서비스 요청을 보내고, 요청의 처리 결과를 나중에 확인할 수 있는 `Future` 객체를 반환받아.

즉, `call_async()`를 호출했다고 해서 순간이동이 이미 완료되었다는 뜻은 아니야.

요청이 전송되고 처리되는 과정이 진행 중일 수 있어.

## 7-2. Future란?

```python
future = self.client.call_async(request)
```

여기서 `future`는 나중에 도착할 결과를 나타내는 객체야.

예를 들어 인터넷으로 어떤 작업을 요청했다고 생각해 보자.

```text
작업 요청
   │
   ▼
처리 중
   │
   ▼
결과 도착
```

요청을 보낸 직후에는 결과가 아직 없을 수 있어.

이때 결과가 준비되었는지 확인할 수 있도록 해 주는 것이 Future라고 이해하면 돼.

ROS 2에서는 다음과 같이 사용할 수 있어.

```python
future.done()
```

요청 처리가 완료되었는지 확인해.

```python
future.result()
```

완료된 요청의 응답 결과를 가져와.

중요한 점은 `future.result()`가 서비스가 반환한 응답 객체를 제공한다는 것이야. 아직 완료되지 않은 Future에서는 일반적으로 결과를 바로 가져올 수 없으므로, 완료 여부를 확인한 뒤 사용해야 해.

---

# 8. 왜 `return`을 사용할까?

현재 코드를 다시 보자.

```python
return self.client.call_async(request)
```

`call_async()`가 반환하는 Future 객체를 `send_request()`의 호출자에게 전달하는 거야.

이후 `main()`에서 다음과 같이 받을 수 있어.

```python
future = node.send_request()
```

실행 과정을 살펴보자.

```text
main()
  │
  ▼
node.send_request()
  │
  ├── 서비스 준비 확인
  ├── Request 생성
  ├── x, y, theta 설정
  └── call_async(request)
          │
          ▼
      Future 반환
          │
          ▼
main()의 future 변수에 저장
```

따라서 다음 두 코드는 서로 연결되어 있어.

함수 내부:

```python
return self.client.call_async(request)
```

함수 호출:

```python
future = node.send_request()
```

함수 내부에서 반환한 Future가 `future` 변수에 저장되는 거야.

---

# 9. `main()` 함수 이해하기

이제 프로그램의 실행 부분을 살펴보자.

```python
def main(args=None):
    """서비스를 호출합니다."""
    rclpy.init(args=args)
    node = TeleportClient()

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
```

## 9-1. ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 프로그램을 초기화해.

일반적으로 노드를 생성하기 전에 실행해야 해.

## 9-2. 노드 생성

```python
node = TeleportClient()
```

`TeleportClient` 객체를 생성해.

이 과정에서 `__init__()`이 실행되고 다음 작업이 수행돼.

- 노드 이름 설정
- 순간이동 서비스 Client 생성

## 9-3. 서비스 요청 전송

```python
future = node.send_request()
```

앞에서 설명한 `send_request()` 함수를 호출해.

이 함수 안에서 서비스가 준비되었는지 확인한 다음 요청 메시지를 만들고, `call_async()`로 요청을 보내.

그리고 Future를 반환해.

## 9-4. 요청 완료까지 기다리기

```python
rclpy.spin_until_future_complete(node, future)
```

이번 실습에서 매우 중요한 코드야.

앞에서 `call_async()`를 사용했기 때문에 서비스 요청의 결과는 나중에 도착할 수 있어.

따라서 응답을 처리할 수 있도록 노드를 실행하면서 Future가 완료될 때까지 기다리는 거야.

전체 흐름은 다음과 같아.

```text
서비스 요청
    │
    ▼
Future 생성
    │
    ▼
spin_until_future_complete()
    │
    ├── 응답 대기
    │
    └── 응답 처리 완료
              │
              ▼
       future.result()
```

### `spin()`과의 차이

이전 실습에서는 다음 코드를 사용했어.

```python
rclpy.spin(node)
```

이 코드는 노드를 계속 실행하면서 콜백을 처리해.

이번에는 다음 코드를 사용해.

```python
rclpy.spin_until_future_complete(node, future)
```

이 코드는 특정 Future의 완료를 기다려.

두 함수의 차이를 정리하면 다음과 같아.

| 함수 | 역할 |
|---|---|
| `rclpy.spin(node)` | 노드를 계속 실행 |
| `rclpy.spin_until_future_complete(node, future)` | 지정한 Future가 완료될 때까지 실행하며 대기 |

이번 실습은 순간이동 요청 한 번을 보내고 그 결과를 확인하는 구조이므로 두 번째 함수가 적합해.

## 9-5. 응답 가져오기

```python
response = future.result()
```

Future가 완료된 후 서비스 응답을 가져오는 코드야.

여기서 `response`는 서비스 서버가 반환한 응답 객체야.

다만 현재 코드에서는 `response`를 가져오기만 하고 실제로 사용하지는 않아.

또한 **Future가 완료되었다는 사실과 서비스가 성공했다는 사실은 구분해야 해.**

Future의 완료는 요청 처리 결과가 돌아왔다는 뜻이고, 실제 서비스 성공 여부는 서비스의 응답 구조와 해당 서비스의 동작을 확인해야 해.

이번 turtlesim의 `TeleportAbsolute` 서비스는 일반적인 성공 여부를 나타내는 별도 `success` 필드를 제공하지 않아. 따라서 응답 객체를 받아도 `response.success`를 확인하는 방식은 사용할 수 없어.

서비스 타입의 정확한 필드 구성은 다음 명령어로 확인할 수 있어.

```bash
ros2 interface show turtlesim/srv/TeleportAbsolute
```

---

# 10. 프로그램 종료 처리

마지막 부분을 보자.

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

이 구조는 앞에서 배운 실습과 같아.

### `KeyboardInterrupt`

```python
except KeyboardInterrupt:
    pass
```

터미널에서 `Ctrl + C`를 누르면 발생할 수 있는 키보드 인터럽트를 처리해.

### `destroy_node()`

```python
node.destroy_node()
```

노드를 정리해.

### `try_shutdown()`

```python
rclpy.try_shutdown()
```

ROS 2의 종료 처리를 시도해.

이렇게 하면 프로그램을 종료할 때 필요한 정리 작업을 수행할 수 있어.

---

# 11. 현재 코드에서 개선하면 좋은 부분

현재 작성한 코드는 실습의 핵심 기능을 잘 구현했어.

다만 두 가지를 개선하면 더 명확하고 안정적인 코드가 돼.

## 개선 1. Docstring 위치 변경

현재 코드:

```python
def send_request(self):
    self.client.wait_for_service()
    """순간이동 요청을 보냅니다."""
```

추천 코드:

```python
def send_request(self):
    """순간이동 요청을 보냅니다."""
    self.client.wait_for_service()
```

함수 설명 문자열은 함수의 첫 번째 문장으로 작성하는 것이 올바른 Python 스타일이야.

## 개선 2. 서비스 준비 대기 시간을 지정하기

현재 코드:

```python
self.client.wait_for_service()
```

이 코드는 서비스가 준비될 때까지 계속 기다릴 수 있어.

실습에서는 괜찮지만, 실제 프로그램에서는 서비스 서버가 실행되지 않는 경우를 처리하는 것이 좋아.

예를 들어 다음과 같이 작성할 수 있어.

```python
if not self.client.wait_for_service(timeout_sec=5.0):
    self.get_logger().error('순간이동 서비스를 찾을 수 없습니다.')
    return None
```

이렇게 하면 5초 동안 서비스를 기다린 후, 준비되지 않았다면 오류 메시지를 출력할 수 있어.

다만 이렇게 수정하면 `send_request()`가 `None`을 반환할 수 있으므로, `main()`에서도 이를 확인해야 해.

---

# 12. 개선된 전체 코드

실습의 원래 구조를 유지하면서 설명과 로그를 추가한 코드야.

```python
"""거북이를 순간이동시키는 서비스 실습입니다."""

import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute


class TeleportClient(Node):
    """순간이동 서비스를 요청하는 노드입니다."""

    def __init__(self):
        super().__init__('lesson_08_teleport_client')

        # 순간이동 서비스 Client 생성
        self.client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

    def send_request(self):
        """순간이동 요청을 보냅니다."""

        # 서비스가 준비될 때까지 최대 5초 대기
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(
                '순간이동 서비스를 찾을 수 없습니다.'
            )
            return None

        # 요청 메시지 생성
        request = TeleportAbsolute.Request()

        # 목표 위치와 방향 설정
        request.x = 2.0
        request.y = 2.0
        request.theta = 0.0

        self.get_logger().info(
            '순간이동 요청: x=2.0, y=2.0, theta=0.0'
        )

        # 비동기 서비스 요청
        return self.client.call_async(request)


def main(args=None):
    """서비스를 호출합니다."""

    rclpy.init(args=args)
    node = TeleportClient()

    try:
        future = node.send_request()

        # 서비스가 준비되지 않았다면 종료
        if future is None:
            return

        # 응답이 도착할 때까지 대기
        rclpy.spin_until_future_complete(node, future)

        # 응답 확인
        response = future.result()

        if response is not None:
            node.get_logger().info(
                '순간이동 서비스 응답을 받았습니다.'
            )
        else:
            node.get_logger().error(
                '서비스 응답을 받지 못했습니다.'
            )

    except KeyboardInterrupt:
        pass
    except Exception as e:
        node.get_logger().error(f'오류 발생: {e}')
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

이 코드는 원래 실습보다 예외 처리를 추가한 버전이야.

다만 서비스 요청이 실제로 처리되었는지 더 자세히 확인하고 싶다면, 실행 후 거북이의 위치를 확인하는 방법도 있어.

---

# 13. Ubuntu에서 직접 실행하기

현재 사용 중인 Ubuntu 24.04와 ROS 2 Jazzy 환경에서 실행하는 방법이야.

### 터미널 1: turtlesim 실행

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

거북이 시뮬레이터가 실행돼.

### 터미널 2: 워크스페이스 빌드

코드가 `turtle_robot` 패키지에 들어 있다고 가정하면 다음과 같이 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 워크스페이스를 적용해.

```bash
source install/setup.bash
```

### 터미널 2: 서비스 Client 실행

`setup.py`의 실행 이름이 `lesson_08_teleport_client`라면 다음과 같이 실행할 수 있어.

```bash
ros2 run turtle_robot lesson_08_teleport_client
```

실행 이름이 다르면 `setup.py`에 등록된 실제 실행 이름을 사용해야 해.

### 터미널 3: 위치 확인

거북이가 실제로 이동했는지 확인하려면 다음 명령어를 사용해.

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /turtle1/pose
```

거북이의 위치가 다음과 비슷하게 바뀌는지 확인해.

```yaml
x: 2.0
y: 2.0
theta: 0.0
```

위치 메시지는 계속 출력되므로 확인이 끝나면 `Ctrl + C`를 눌러 종료하면 돼.

---

# 14. 이번 실습에서 꼭 기억해야 할 핵심 5가지

| 개념 | 코드 | 의미 |
|---|---|---|
| Client 생성 | `create_client()` | 서비스를 호출할 준비 |
| 서비스 대기 | `wait_for_service()` | 서비스 서버가 준비되었는지 확인 |
| 요청 생성 | `TeleportAbsolute.Request()` | 요청 메시지 생성 |
| 요청 전송 | `call_async(request)` | 비동기로 서비스 요청 |
| 응답 대기 | `spin_until_future_complete()` | Future가 완료될 때까지 기다림 |

그리고 다음 네 줄은 반드시 이해하고 넘어가면 좋아.

```python
request = TeleportAbsolute.Request()
request.x = 2.0
request.y = 2.0
request.theta = 0.0
```

이 코드는 서비스에 전달할 요청 메시지를 만드는 과정이야.

```python
return self.client.call_async(request)
```

이 코드는 요청을 보내고 Future를 반환하는 과정이야.

```python
rclpy.spin_until_future_complete(node, future)
```

이 코드는 요청의 처리 결과를 기다리는 과정이야.

```python
response = future.result()
```

이 코드는 완료된 Future에서 응답을 가져오는 과정이야.

**이번 실습의 가장 중요한 개념은 Service Client가 요청을 보내고 Future를 통해 처리 결과를 확인한다는 것**이야.

