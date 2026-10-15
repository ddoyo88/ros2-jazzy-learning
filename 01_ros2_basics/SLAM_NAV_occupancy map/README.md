
## 1. 프로그램이 어떻게 동작할까?

전체적인 데이터 흐름은 다음과 같아.

```text
┌──────────────────────────────────────┐
│ ROS 2 노드                           │
│ occupancy_grid_publisher             │
│                                      │
│  ① 0.5초마다 타이머 실행             │
│                ↓                     │
│  ② OccupancyGrid 메시지 생성         │
│                ↓                     │
│  ③ 지도 정보와 셀 데이터 입력        │
│                ↓                     │
│  ④ 메시지 발행                       │
└──────────────────┬───────────────────┘
                   │
                   ▼
       /custom_occupancy_grid
                   │
          ┌────────┴─────────┐
          ▼                  ▼
    ros2 topic echo        RViz2
    데이터 확인            지도 시각화
```

여기서 기억해야 할 핵심 용어는 다섯 가지야.

| 용어 | 의미 |
|---|---|
| Node | 특정 작업을 수행하는 ROS 2 프로그램 |
| Publisher | 토픽으로 데이터를 발행하는 기능 |
| Topic | 노드들이 데이터를 주고받는 통신 경로 |
| Message | 토픽을 통해 전달하는 데이터 형식 |
| Timer | 일정한 시간 간격으로 함수를 실행하는 기능 |

이번 실습에서는 `occupancy_grid_publisher` 노드가 `custom_occupancy_grid` 토픽으로 지도 데이터를 발행해.

---

# 2. 패키지 만들기

먼저 터미널에서 ROS 2 환경을 설정하고 워크스페이스로 이동하자.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws/src
```

패키지를 생성해.

```bash
ros2 pkg create simple_nav --build-type ament_python --dependencies rclpy nav_msgs
```

## 2-1. 명령어의 의미

### `ros2 pkg create`

ROS 2 패키지를 생성하는 명령어야.

패키지는 ROS 2 프로그램을 관리하는 기본 단위라고 생각하면 돼. 노드 코드와 설정 파일, 의존성 정보 등을 패키지에 담아 관리해.

### `simple_nav`

우리가 만들 패키지의 이름이야.

`simple_nav`는 Simple Navigation, 즉 간단한 내비게이션을 의미하도록 정한 이름이야.

### `--build-type ament_python`

이 패키지를 Python 기반으로 빌드하겠다는 뜻이야.

ROS 2 패키지는 C++용인 `ament_cmake`, Python용인 `ament_python` 등의 빌드 방식을 사용할 수 있어.

이번 코드는 Python으로 작성했기 때문에 `ament_python`을 사용해.

### `--dependencies rclpy nav_msgs`

프로그램에서 필요한 ROS 2 라이브러리를 선언하는 부분이야.

- `rclpy`: Python으로 ROS 2 노드를 작성하는 데 사용하는 라이브러리
- `nav_msgs`: `OccupancyGrid` 등 지도와 관련된 메시지 형식을 제공하는 패키지

예를 들어 다음 코드를 실행하려면 `rclpy`가 필요해.

```python
import rclpy
from rclpy.node import Node
```

다음 코드를 실행하려면 `nav_msgs`가 필요하지.

```python
from nav_msgs.msg import OccupancyGrid
```

## 2-2. 패키지가 생성되면?

다음과 비슷한 구조가 만들어져.

```text
ros2_ws/
└── src/
    └── simple_nav/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── simple_nav
        ├── simple_nav/
        │   └── __init__.py
        └── test/
```

여기서 중요한 파일은 다음과 같아.

| 파일 | 역할 |
|---|---|
| `package.xml` | 패키지 정보와 의존성 선언 |
| `setup.py` | Python 패키지 설치 및 실행 명령 설정 |
| `setup.cfg` | Python 실행 파일의 설치 위치 등 설정 |
| `simple_nav/__init__.py` | Python 패키지임을 표시 |
| `simple_nav/` 안의 Python 파일 | 실제 ROS 2 노드 코드 |

**주의:** `pub_occupancy_grid.py`는 바깥쪽 `simple_nav` 폴더가 아니라, 안쪽 Python 패키지 폴더에 저장해야 해.

정확한 경로는 다음과 같아.

```text
~/ros2_ws/src/simple_nav/simple_nav/pub_occupancy_grid.py
```

---

# 3. 먼저 `OccupancyGrid` 메시지 이해하기

코드를 이해하려면 가장 먼저 지도 데이터의 구조를 알아야 해.

`OccupancyGrid`는 2D 격자 지도를 표현하기 위한 ROS 2 메시지 형식이야.

예를 들어 로봇이 다음과 같은 공간을 이동한다고 가정해 보자.

```text
┌─────┬─────┬─────┬─────┐
│ 100 │  0  │  0  │  0  │
├─────┼─────┼─────┼─────┤
│  0  │ -1  │  0  │  0  │
├─────┼─────┼─────┼─────┤
│ -1  │  0  │ 100 │  0  │
├─────┼─────┼─────┼─────┤
│ -1  │  0  │ 100 │  0  │
└─────┴─────┴─────┴─────┘
```

각 칸은 지도의 작은 셀 하나를 의미해.

일반적으로 `OccupancyGrid`의 셀 값은 다음과 같이 해석해.

| 값 | 일반적인 의미 |
|---:|---|
| `0` | 비어 있는 공간 |
| `100` | 장애물이 있는 공간 |
| `-1` | 알 수 없는 공간 |

중간 값인 `1`부터 `99`까지는 확률적 점유 정보를 표현할 때 사용할 수 있어.

다만 이 값은 메시지에 저장되는 데이터야. **RViz2에서 어떻게 색으로 보이는지는 표시 설정과 사용하는 디스플레이에 따라서도 달라질 수 있어.**

## 3-1. 지도 데이터는 왜 1차원 배열일까?

지도는 2차원으로 보이지만, 메시지의 `data` 필드는 1차원 배열이야.

예를 들어 가로 4칸, 세로 4칸인 지도는 다음과 같아.

```text
        가로 방향 →
       0    1    2    3
     ┌────┬────┬────┬────┐
  0  │ 100│  0 │  0 │  0 │
     ├────┼────┼────┼────┤
  1  │  0 │ -1 │  0 │  0 │
     ├────┼────┼────┼────┤
  2  │ -1 │  0 │ 100│  0 │
     ├────┼────┼────┼────┤
  3  │ -1 │  0 │ 100│  0 │
     └────┴────┴────┴────┘
       ↑
      세로 방향
```

이 데이터를 행 단위로 펼치면 다음과 같은 배열이 돼.

```python
[
    100, 0, 0, 0,
    0, -1, 0, 0,
    -1, 0, 100, 0,
    -1, 0, 100, 0
]
```

즉, 첫 번째 행의 4개 셀을 저장하고, 두 번째 행의 4개 셀을 저장하는 방식이야.

지도 전체 셀 개수는 다음 공식으로 계산할 수 있어.

\[
\text{셀 개수} = \text{width} \times \text{height}
\]

따라서 가로 4칸, 세로 4칸이면 다음과 같아.

\[
4 \times 4 = 16
\]

그러므로 `data` 배열에는 정확히 16개의 값이 있어야 해.

이 부분은 나중에 SLAM, 지도 작성, 경로 계획을 공부할 때도 계속 사용하게 돼.

---

# 4. Python 노드 코드 한 줄씩 이해하기

이번에는 실습에서 요구한 **가로 4칸, 세로 4칸인 지도**를 발행하는 완성 코드를 먼저 살펴보자.

파일 경로:

```text
~/ros2_ws/src/simple_nav/simple_nav/pub_occupancy_grid.py
```

## 4-1. 완성 코드

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid


class OccupancyGridPublisher(Node):

    def __init__(self):
        super().__init__('occupancy_grid_publisher')

        # 1. OccupancyGrid 메시지를 발행할 Publisher 생성
        self.og_pub = self.create_publisher(
            OccupancyGrid,
            'custom_occupancy_grid',
            10
        )

        # 2. 0.5초마다 og_callback() 실행
        self.timer = self.create_timer(
            0.5,
            self.og_callback
        )

    def og_callback(self):
        # 3. OccupancyGrid 메시지 객체 생성
        occupancy_grid_msg = OccupancyGrid()

        # 4. Header 설정
        occupancy_grid_msg.header.stamp = (
            self.get_clock().now().to_msg()
        )
        occupancy_grid_msg.header.frame_id = 'map_frame'

        # 5. 지도 메타데이터 설정
        occupancy_grid_msg.info.resolution = 1.0
        occupancy_grid_msg.info.width = 4
        occupancy_grid_msg.info.height = 4

        # 6. 지도 원점 설정
        occupancy_grid_msg.info.origin.position.x = 0.0
        occupancy_grid_msg.info.origin.position.y = 0.0
        occupancy_grid_msg.info.origin.position.z = 0.0

        occupancy_grid_msg.info.origin.orientation.x = 0.0
        occupancy_grid_msg.info.origin.orientation.y = 0.0
        occupancy_grid_msg.info.origin.orientation.z = 0.0
        occupancy_grid_msg.info.origin.orientation.w = 1.0

        # 7. 4x4 지도 데이터 설정
        occupancy_grid_msg.data = [
            100, 0, 0, 0,
            0, -1, 0, 0,
            -1, 0, 100, 0,
            -1, 0, 100, 0
        ]

        # 8. 지도 메시지 발행
        self.og_pub.publish(occupancy_grid_msg)

        self.get_logger().info(
            'Publishing Custom Occupancy Grid...'
        )


def main(args=None):
    # ROS 2 초기화
    rclpy.init(args=args)

    # 노드 객체 생성
    node = OccupancyGridPublisher()

    try:
        # 콜백과 타이머가 실행되도록 대기
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # 노드 종료 및 ROS 2 정리
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

이제 중요한 부분을 순서대로 살펴보자.

## 4-2. 라이브러리 불러오기

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
```

### `#!/usr/bin/env python3`

```python
#!/usr/bin/env python3
```

이 줄은 셔뱅(shebang)이라고 해.

파일을 실행할 때 어떤 인터프리터를 사용할지 운영체제에 알려주는 역할을 해.

여기서는 Python 3을 사용하라는 뜻이야.

ROS 2에서 `ros2 run`으로 실행할 때는 패키지의 설치 설정이 중요하므로, 이 줄만 작성했다고 실행 파일이 자동으로 등록되는 것은 아니야.

### `import rclpy`

```python
import rclpy
```

Python에서 ROS 2 기능을 사용하기 위해 `rclpy`를 불러와.

예를 들어 다음 기능을 사용하려면 필요해.

```python
rclpy.init()
rclpy.spin(node)
rclpy.shutdown()
```

각 기능의 역할은 뒤에서 설명할게.

### `from rclpy.node import Node`

```python
from rclpy.node import Node
```

ROS 2 노드를 만들기 위한 `Node` 클래스를 가져와.

노드는 ROS 2에서 하나의 독립적인 작업 단위야.

예를 들어 다음과 같은 작업들이 각각 노드가 될 수 있어.

- 카메라 영상을 발행하는 노드
- 로봇의 위치를 계산하는 노드
- 장애물 지도를 발행하는 노드
- 로봇의 이동 명령을 발행하는 노드

이번 실습에서는 지도 메시지를 발행하는 노드를 만들 거야.

### `from nav_msgs.msg import OccupancyGrid`

```python
from nav_msgs.msg import OccupancyGrid
```

지도 메시지 형식인 `OccupancyGrid`를 가져오는 코드야.

이 메시지는 단순히 셀 데이터만 담는 게 아니야. 지도 크기, 셀의 실제 크기, 지도 원점, 좌표계 정보 등을 함께 담을 수 있어.

메시지 구조를 간단히 표현하면 다음과 같아.

```text
OccupancyGrid
├── header
│   ├── stamp
│   └── frame_id
│
├── info
│   ├── resolution
│   ├── width
│   ├── height
│   └── origin
│
└── data
    ├── 셀 0
    ├── 셀 1
    ├── 셀 2
    └── ...
```

이 구조를 기억하면 뒤에 나오는 코드가 훨씬 이해하기 쉬워져.

---

## 4-3. 클래스와 생성자

```python
class OccupancyGridPublisher(Node):
```

이 코드는 `OccupancyGridPublisher`라는 클래스를 정의해.

괄호 안에 `Node`가 있다는 점이 중요해.

```python
class OccupancyGridPublisher(Node):
```

이것은 `OccupancyGridPublisher`가 ROS 2의 `Node` 클래스를 상속한다는 뜻이야.

상속을 이용하면 `Node`에서 제공하는 기능을 사용할 수 있어.

예를 들어 다음과 같은 기능이 있어.

```python
self.create_publisher()
self.create_timer()
self.get_clock()
self.get_logger()
```

따라서 매번 이런 기능을 처음부터 만들 필요가 없어.

### 생성자 `__init__()`

```python
def __init__(self):
    super().__init__('occupancy_grid_publisher')
```

`__init__()`은 객체가 만들어질 때 실행되는 초기화 함수야.

다음 코드를 실행하면,

```python
node = OccupancyGridPublisher()
```

Python이 객체를 생성하면서 `__init__()`을 실행해.

그 안의 다음 코드도 실행되지.

```python
super().__init__('occupancy_grid_publisher')
```

여기서 `super().__init__()`은 부모 클래스인 `Node`의 초기화 기능을 호출해.

그리고 다음 문자열은 ROS 2 노드의 이름이야.

```python
'occupancy_grid_publisher'
```

따라서 실행 후 다음 명령어로 노드를 확인할 수 있어.

```bash
ros2 node list
```

출력 예시:

```text
/occupancy_grid_publisher
```

**정리:** 클래스는 노드의 설계도이고, 생성자는 실제 노드 객체가 만들어질 때 필요한 초기 설정을 수행해.

---

# 5. Publisher 생성하기

```python
self.og_pub = self.create_publisher(
    OccupancyGrid,
    'custom_occupancy_grid',
    10
)
```

이 코드는 이번 실습의 핵심 중 하나야.

ROS 2에서 메시지를 발행할 Publisher를 생성해.

## 5-1. `create_publisher()`의 의미

일반적인 형태는 다음과 같아.

```python
self.create_publisher(
    메시지_형식,
    토픽_이름,
    큐_크기
)
```

이번 실습에서는 다음과 같이 작성했어.

```python
self.og_pub = self.create_publisher(
    OccupancyGrid,
    'custom_occupancy_grid',
    10
)
```

각 인자의 역할을 살펴보자.

| 코드 | 의미 |
|---|---|
| `OccupancyGrid` | 발행할 메시지 형식 |
| `'custom_occupancy_grid'` | 메시지를 발행할 토픽 이름 |
| `10` | QoS 설정에서 사용하는 큐 깊이 |

### 첫 번째 인자: `OccupancyGrid`

```python
OccupancyGrid
```

지도 데이터를 발행하겠다는 뜻이야.

다음처럼 다른 메시지 형식을 사용할 수도 있어.

```python
Twist
```

`Twist`는 선속도와 각속도 등의 이동 명령을 표현할 때 사용하는 메시지 형식이야.

예를 들어 네가 앞에서 공부한 turtlesim 실습에서는 다음과 같이 사용했지.

```python
self.cmd_vel_pub = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

이번 실습은 이동 명령이 아니라 지도를 발행하므로 `OccupancyGrid`를 사용해.

### 두 번째 인자: 토픽 이름

```python
'custom_occupancy_grid'
```

메시지가 전달될 통신 경로의 이름이야.

이 Publisher가 발행한 메시지는 다음 토픽으로 전달돼.

```text
/custom_occupancy_grid
```

앞에 `/`를 명시하지 않아도 기본 네임스페이스에서 실행하면 일반적으로 `/custom_occupancy_grid`로 확인할 수 있어.

다음 명령어로 토픽을 확인할 수 있어.

```bash
ros2 topic list
```

### 세 번째 인자: `10`

```python
10
```

이 숫자는 Publisher의 QoS 설정에서 사용하는 큐 깊이야.

간단히 말해, 메시지가 전달되는 과정에서 대기할 수 있도록 설정하는 큐의 크기와 관련 있어.

다만 `10`이 모든 상황에서 메시지 10개를 무조건 저장하거나 보장한다는 뜻은 아니야. 실제 동작은 QoS 정책과 통신 상황에 따라 달라져.

### 왜 변수에 저장할까?

```python
self.og_pub = ...
```

생성한 Publisher 객체를 `self.og_pub`이라는 변수에 저장하는 거야.

나중에 메시지를 발행할 때 이 변수를 사용해.

```python
self.og_pub.publish(occupancy_grid_msg)
```

만약 Publisher를 생성하기만 하고 변수에 저장하지 않는다면, 뒤에서 그 Publisher를 통해 메시지를 발행하기가 어려워져.

**핵심:** `create_publisher()`는 발행 기능을 만들고, `publish()`는 실제 메시지를 발행해.

---

# 6. Timer 설정하기

```python
self.timer = self.create_timer(
    0.5,
    self.og_callback
)
```

이 코드는 0.5초마다 `og_callback()` 함수를 실행하도록 타이머를 설정해.

## 6-1. `create_timer()`의 구조

```python
self.create_timer(시간_간격, 실행할_함수)
```

이번 코드에서는 다음과 같아.

```python
self.create_timer(0.5, self.og_callback)
```

- `0.5`: 실행 간격을 초 단위로 지정
- `self.og_callback`: 실행할 콜백 함수

0.5초는 500밀리초야.

따라서 명목상 초당 두 번 메시지를 발행하게 돼.

\[
\text{초당 발행 횟수} = \frac{1}{0.5} = 2
\]

실제 실행 간격은 시스템 부하나 ROS 2 실행 상태에 따라 조금 달라질 수 있어.

### 왜 타이머가 필요할까?

타이머가 없다면 `og_callback()`을 직접 호출하도록 코드를 작성해야 해.

하지만 타이머를 사용하면 ROS 2가 설정한 간격에 맞춰 콜백 실행을 관리해 줘.

이번 실습에서는 다음 순서가 반복돼.

```text
0.0초: 타이머 대기
0.5초: og_callback() 실행
1.0초: og_callback() 실행
1.5초: og_callback() 실행
2.0초: og_callback() 실행
...
```

### `self.og_callback` 뒤에 괄호가 없는 이유

다음 두 코드는 의미가 달라.

```python
self.create_timer(0.5, self.og_callback)
```

```python
self.create_timer(0.5, self.og_callback())
```

첫 번째는 함수 자체를 전달해. 타이머가 실행할 때 해당 함수를 호출하도록 하는 방식이야.

두 번째는 `og_callback()`을 그 자리에서 호출한 다음, 그 반환값을 전달하려는 형태가 돼. 이 실습에서 원하는 동작이 아니야.

따라서 **괄호 없이 `self.og_callback`이라고 작성해야 해.**

---

# 7. 콜백 함수에서 지도 메시지 만들기

이제 `og_callback()`을 살펴보자.

```python
def og_callback(self):
    occupancy_grid_msg = OccupancyGrid()
```

## 7-1. `og_callback()`은 무엇일까?

```python
def og_callback(self):
```

`og_callback`이라는 함수를 정의한 거야.

여기서 콜백(callback)은 특정 이벤트가 발생했을 때 실행되는 함수를 의미해.

이번 실습에서는 타이머가 실행 시점을 결정해.

```python
self.timer = self.create_timer(0.5, self.og_callback)
```

따라서 타이머가 실행되면 `og_callback()`이 호출돼.

함수 안에서는 지도 메시지를 생성하고, 필요한 데이터를 채우고, 토픽으로 발행해.

## 7-2. 메시지 객체 생성

```python
occupancy_grid_msg = OccupancyGrid()
```

이 코드는 `OccupancyGrid` 형식의 메시지 객체를 하나 생성해.

쉽게 말하면 **지도 데이터를 담을 빈 상자를 만드는 것**이야.

```text
occupancy_grid_msg
        │
        └── OccupancyGrid 메시지
             ├── header
             ├── info
             └── data
```

이제 이 객체 안에 지도와 관련된 값을 채워 넣으면 돼.

여기서 알아둘 점은 타이머가 실행될 때마다 새로운 메시지 객체를 만든다는 거야.

```python
def og_callback(self):
    occupancy_grid_msg = OccupancyGrid()
```

이렇게 하면 각 콜백 실행에서 새 메시지를 구성해 발행할 수 있어.

---

# 8. Header 설정하기

```python
occupancy_grid_msg.header.stamp = (
    self.get_clock().now().to_msg()
)

occupancy_grid_msg.header.frame_id = 'map_frame'
```

Header는 메시지에 관한 기본적인 메타정보를 담는 부분이야.

이번 코드에서는 두 가지 정보를 설정해.

1. 메시지를 만든 시각
2. 메시지 데이터가 기준으로 삼는 좌표계의 이름

## 8-1. 현재 시간 설정

```python
occupancy_grid_msg.header.stamp = (
    self.get_clock().now().to_msg()
)
```

조금 복잡해 보이지만 순서대로 이해하면 돼.

### 첫 번째: `self.get_clock()`

```python
self.get_clock()
```

현재 노드에서 사용하는 ROS 2 시계 객체를 가져와.

### 두 번째: `.now()`

```python
self.get_clock().now()
```

현재 시각을 가져와.

ROS 2에서는 노드의 시계 설정에 따라 실제 시스템 시간 대신 시뮬레이션 시간 등을 사용할 수도 있어.

### 세 번째: `.to_msg()`

```python
self.get_clock().now().to_msg()
```

가져온 시간을 ROS 2 메시지에서 사용하는 시간 형식으로 변환해.

### 네 번째: `header.stamp`에 저장

```python
occupancy_grid_msg.header.stamp = (
    self.get_clock().now().to_msg()
)
```

이제 메시지의 Header에 현재 시각이 기록돼.

정리하면 다음과 같아.

```text
현재 시각 가져오기
       ↓
ROS 2 메시지 시간 형식으로 변환
       ↓
header.stamp에 저장
```

이 시간 정보는 여러 센서 데이터를 비교하거나, 시간에 맞춰 데이터를 처리할 때 중요해.

## 8-2. 좌표계 이름 설정

```python
occupancy_grid_msg.header.frame_id = 'map_frame'
```

여기서는 지도 데이터의 기준 좌표계 이름을 `map_frame`으로 설정했어.

ROS 2에서 `frame_id`는 메시지가 어떤 좌표계를 기준으로 표현되는지 나타내는 문자열이야.

예를 들어 다음과 같은 좌표계 이름을 자주 볼 수 있어.

| 좌표계 이름 | 일반적인 용도 |
|---|---|
| `map` | 전역 지도 좌표계 |
| `odom` | 오도메트리 좌표계 |
| `base_link` | 로봇 본체의 기준 좌표계 |
| `laser` 또는 `laser_frame` | 레이저 센서 좌표계 |

이번 실습에서는 예제에 맞춰 `map_frame`을 사용한 거야.

단, `map_frame`이라고 적었다고 해서 좌표계가 자동으로 생성되는 것은 아니야. 다른 노드나 RViz2에서 이 프레임을 사용하려면 해당 프레임을 인식할 수 있도록 설정해야 해.

**실습에서는 `map_frame`을 그대로 사용해도 되지만, 실제 내비게이션 시스템에서는 좌표계 이름과 TF(Transform) 설정을 일치시키는 것이 중요해.**

---

# 9. 지도 메타데이터 설정하기

```python
occupancy_grid_msg.info.resolution = 1.0
occupancy_grid_msg.info.width = 4
occupancy_grid_msg.info.height = 4
```

이 세 가지는 지도 자체의 구조를 정의해.

## 9-1. `resolution`: 셀 하나의 실제 크기

```python
occupancy_grid_msg.info.resolution = 1.0
```

`resolution`은 지도 셀 하나가 실제 공간에서 어느 정도 크기인지 나타내.

단위는 **미터(m)** 야.

이번 설정은 다음과 같아.

```python
resolution = 1.0
```

즉, 셀 하나의 가로·세로 크기가 각각 1m라는 뜻이야.

```text
셀 하나
┌──────────┐
│          │  1m
│          │
└──────────┘
    1m
```

만약 다음처럼 설정하면,

```python
occupancy_grid_msg.info.resolution = 0.05
```

셀 하나의 크기는 0.05m, 즉 5cm가 돼.

실제 로봇의 지도에서는 공간을 더 세밀하게 표현하기 위해 0.05m 같은 해상도를 사용할 수 있어.

해상도가 작아지면 같은 실제 공간을 표현할 때 더 많은 셀이 필요해져.

## 9-2. `width`: 지도 가로 크기

```python
occupancy_grid_msg.info.width = 4
```

가로 방향으로 셀이 몇 개 있는지 설정해.

여기서는 가로 4칸이야.

```text
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │
└─────┴─────┴─────┴─────┘
```

## 9-3. `height`: 지도 세로 크기

```python
occupancy_grid_msg.info.height = 4
```

세로 방향으로 셀이 몇 개 있는지 설정해.

여기서는 세로 4칸이야.

```text
┌─────┐
│  1  │
├─────┤
│  2  │
├─────┤
│  3  │
├─────┤
│  4  │
└─────┘
```

## 9-4. 지도 전체 크기 계산

실제 지도의 가로·세로 크기는 다음 공식으로 계산할 수 있어.

\[
\text{가로 길이} = \text{resolution} \times \text{width}
\]

\[
\text{세로 길이} = \text{resolution} \times \text{height}
\]

이번 설정에서는 다음과 같아.

- `resolution = 1.0m`
- `width = 4`
- `height = 4`

따라서,

\[
\text{가로 길이} = 1.0 \times 4 = 4m
\]

\[
\text{세로 길이} = 1.0 \times 4 = 4m
\]

즉, **실제 공간에서 가로 4m, 세로 4m에 해당하는 지도를 표현하는 것**이야.

| 설정 | 값 | 의미 |
|---|---:|---|
| `resolution` | 1.0 | 셀 하나가 1m |
| `width` | 4 | 가로 4칸 |
| `height` | 4 | 세로 4칸 |
| 전체 셀 수 | 16 | 4 × 4 |
| 지도 가로 길이 | 4m | 1m × 4 |
| 지도 세로 길이 | 4m | 1m × 4 |

여기서 주의할 점이 있어.

**`width`와 `height`는 미터 단위의 길이가 아니라 셀의 개수야.** 실제 길이는 `resolution`을 곱해서 계산해.

---

# 10. 지도 원점과 방향 설정하기

실습에서 제공한 코드는 다음과 같아.

```python
occupancy_grid_msg.info.origin.position.x = 0.0
occupancy_grid_msg.info.origin.position.y = 0.0
occupancy_grid_msg.info.origin.position.z = 0.0

occupancy_grid_msg.info.origin.orientation.x = 0.0
occupancy_grid_msg.info.origin.orientation.y = 0.0
occupancy_grid_msg.info.origin.orientation.z = 0.0
occupancy_grid_msg.info.origin.orientation.w = 1.0
```

처음 보면 길지만, 크게 두 부분으로 나누면 돼.

- `position`: 지도 원점의 위치
- `orientation`: 지도 원점의 방향

## 10-1. 원점의 위치

```python
occupancy_grid_msg.info.origin.position.x = 0.0
occupancy_grid_msg.info.origin.position.y = 0.0
occupancy_grid_msg.info.origin.position.z = 0.0
```

지도 원점의 위치를 설정하는 코드야.

여기서는 다음과 같이 설정했어.

```text
x = 0.0
y = 0.0
z = 0.0
```

즉, 지도 원점의 위치를 기준 좌표계에서 `(0, 0, 0)`으로 설정한 거야.

다만 원점은 지도에서 첫 번째 셀이 시작하는 위치를 결정하는 개념이므로, 단순히 RViz 화면의 중앙이라는 뜻은 아니야.

## 10-2. 원점의 방향

```python
occupancy_grid_msg.info.origin.orientation.x = 0.0
occupancy_grid_msg.info.origin.orientation.y = 0.0
occupancy_grid_msg.info.origin.orientation.z = 0.0
occupancy_grid_msg.info.origin.orientation.w = 1.0
```

여기서는 지도 원점의 방향을 쿼터니언(quaternion)으로 설정하고 있어.

ROS 2에서는 3차원 회전 방향을 표현하기 위해 쿼터니언을 사용해.

쿼터니언은 네 개의 값으로 구성돼.

```text
x, y, z, w
```

이번 실습의 값은 다음과 같아.

```text
x = 0
y = 0
z = 0
w = 1
```

이 값은 **회전이 없는 기본 방향, 즉 단위 회전**을 의미해.

처음 공부할 때는 다음과 같이 기억하면 돼.

```python
orientation.x = 0.0
orientation.y = 0.0
orientation.z = 0.0
orientation.w = 1.0
```

이 설정은 지도 원점에 별도의 회전을 적용하지 않는다는 뜻이야.

나중에 로봇의 자세, IMU, TF, 쿼터니언을 공부할 때 더 깊게 이해하면 돼.

---

# 11. 지도 데이터 `data` 채우기

```python
occupancy_grid_msg.data = [
    100, 0, 0, 0,
    0, -1, 0, 0,
    -1, 0, 100, 0,
    -1, 0, 100, 0
]
```

이 코드는 실제 셀별 지도 정보를 입력하는 부분이야.

앞에서 `width`와 `height`를 4로 설정했으므로, 셀은 총 16개야.

```python
width = 4
height = 4
```

따라서 `data` 배열에도 16개의 값이 있어야 해.

## 11-1. 데이터를 2차원으로 해석하기

현재 데이터는 다음과 같아.

```python
[
    100, 0, 0, 0,
    0, -1, 0, 0,
    -1, 0, 100, 0,
    -1, 0, 100, 0
]
```

이 배열을 4개씩 나누면 다음과 같이 볼 수 있어.

```text
행 0: 100   0   0   0
행 1:   0  -1   0   0
행 2:  -1   0 100   0
행 3:  -1   0 100   0
```

일반적인 `OccupancyGrid` 데이터는 행 단위로 저장되며, 인덱스는 다음과 같이 계산할 수 있어.

\[
\text{index} = x + y \times \text{width}
\]

여기서 `x`는 가로 방향 셀 인덱스, `y`는 세로 방향 셀 인덱스야.

예를 들어 `width = 4`일 때:

- `(0, 0)` → 인덱스 0
- `(1, 0)` → 인덱스 1
- `(0, 1)` → 인덱스 4
- `(2, 2)` → 인덱스 10

따라서 다음 코드는,

```python
occupancy_grid_msg.data[10] = 100
```

그리드의 `(2, 2)` 위치에 해당하는 셀을 점유된 공간으로 설정하는 거야.

좌표계에서 실제 미터 단위의 위치로 바꾸려면 `origin`과 `resolution`도 함께 고려해야 해.

## 11-2. 왜 `100`, `0`, `-1`을 사용할까?

```python
100
```

점유된 공간을 나타내는 값이야. 일반적으로 장애물이 있는 셀로 해석해.

```python
0
```

비어 있는 공간을 나타내는 값이야.

```python
-1
```

아직 정보를 알 수 없는 공간을 나타내는 값이야.

예를 들어 다음 데이터는,

```python
occupancy_grid_msg.data = [
    100, 0, 0, 0,
    0, -1, 0, 0,
    -1, 0, 100, 0,
    -1, 0, 100, 0
]
```

일부 셀에는 장애물 정보가 있고, 일부 셀은 비어 있으며, 일부 셀은 아직 알 수 없는 상태라는 의미야.

다만 이번 데이터는 직접 입력한 예제일 뿐이야. 실제 센서가 장애물을 탐지하거나 SLAM으로 지도를 생성한 것은 아니야.

---

# 12. 메시지 발행하기

```python
self.og_pub.publish(occupancy_grid_msg)
```

이 코드가 실제로 지도 메시지를 토픽으로 발행하는 부분이야.

앞에서 다음 두 가지를 설정했지.

```python
self.og_pub = self.create_publisher(
    OccupancyGrid,
    'custom_occupancy_grid',
    10
)
```

그리고,

```python
occupancy_grid_msg = OccupancyGrid()
```

이제 `occupancy_grid_msg` 안에 지도 정보를 모두 채웠으니 Publisher를 이용해 발행하면 돼.

```python
self.og_pub.publish(occupancy_grid_msg)
```

전체 과정을 연결하면 다음과 같아.

```text
OccupancyGrid 객체 생성
        ↓
Header 설정
        ↓
해상도·너비·높이 설정
        ↓
원점 설정
        ↓
data 배열 설정
        ↓
publish() 호출
        ↓
/custom_occupancy_grid 토픽으로 발행
```

## 12-1. 로그 출력

```python
self.get_logger().info(
    'Publishing Custom Occupancy Grid...'
)
```

이 코드는 터미널에 진행 상황을 출력해.

예를 들어 다음과 같이 표시될 수 있어.

```text
[INFO] [occupancy_grid_publisher]: Publishing Custom Occupancy Grid...
```

여기서 `INFO`는 일반적인 정보 로그를 의미해.

중요한 점은 로그가 출력된다고 해서 RViz2에서 반드시 지도가 보인다는 뜻은 아니라는 거야. 메시지가 발행되었는지와 RViz2가 그 메시지를 올바르게 표시하는지는 별도로 확인해야 해.

---

# 13. `main()` 함수 이해하기

이제 프로그램의 마지막 부분이야.

```python
def main(args=None):
    rclpy.init(args=args)

    node = OccupancyGridPublisher()

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

이 부분은 ROS 2 프로그램을 시작하고 종료하는 역할을 해.

## 13-1. ROS 2 초기화

```python
rclpy.init(args=args)
```

ROS 2 Python 클라이언트를 초기화하는 코드야.

ROS 2 노드를 생성하고 통신 기능을 사용하기 전에 호출해야 해.

## 13-2. 노드 객체 생성

```python
node = OccupancyGridPublisher()
```

앞에서 정의한 클래스를 실제로 실행할 노드 객체로 만들어.

이 시점에 `__init__()`이 실행되면서 다음 작업들이 이루어져.

1. 노드 이름 설정
2. Publisher 생성
3. 타이머 생성

즉, 이 코드가 실행되면 노드가 지도 발행을 준비하게 돼.

## 13-3. `rclpy.spin(node)`

```python
rclpy.spin(node)
```

이 코드는 노드가 콜백을 처리할 수 있도록 계속 실행 상태를 유지해.

이번 실습에서 중요한 이유는 타이머 때문이야.

```python
self.timer = self.create_timer(0.5, self.og_callback)
```

`spin()`이 실행되어야 타이머 콜백이 처리될 수 있어.

이 코드가 없다면 프로그램이 정상적인 실행 루프를 유지하지 못하고 종료될 수 있어.

## 13-4. `try`, `except`, `finally`

```python
try:
    rclpy.spin(node)

except KeyboardInterrupt:
    pass

finally:
    node.destroy_node()
    rclpy.shutdown()
```

각 부분은 다음 역할을 해.

| 코드 | 역할 |
|---|---|
| `try` | 정상 실행할 코드를 실행 |
| `except KeyboardInterrupt` | 사용자가 `Ctrl+C`로 중단했을 때 처리 |
| `pass` | 별도의 작업 없이 넘어감 |
| `finally` | 종료 과정에서 정리 작업 수행 |

마지막의 두 줄이 중요해.

```python
node.destroy_node()
rclpy.shutdown()
```

- `destroy_node()`: 노드 객체를 정리
- `rclpy.shutdown()`: ROS 2 Python 클라이언트의 실행을 종료

**핵심:** `main()`은 ROS 2를 초기화하고, 노드를 실행하며, 종료할 때 필요한 정리 작업을 수행하는 부분이야.

---

# 14. `package.xml` 자세히 이해하기

`package.xml`은 패키지의 이름, 버전, 의존성, 빌드 방식을 기록하는 파일이야.

ROS 2가 패키지를 관리할 때 참고하는 중요한 설정 파일이지.

이번 실습의 내용을 정리한 예제는 다음과 같아.

```xml
<?xml version="1.0"?>
<package format="3">
  <name>simple_nav</name>
  <version>0.0.0</version>
  <description>Occupancy Grid Publisher in Python for ROS 2 Jazzy</description>

  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <depend>rclpy</depend>
  <depend>nav_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

실제로는 `ros2 pkg create`가 생성한 `package.xml`을 기반으로 필요한 부분만 수정해도 돼. 기존 파일을 통째로 교체할 필요는 없어.

## 14-1. XML 선언

```xml
<?xml version="1.0"?>
```

이 파일이 XML 형식으로 작성되었다는 것을 나타내.

## 14-2. 패키지 형식

```xml
<package format="3">
```

ROS 2 패키지 설명 파일의 형식을 지정해.

여기서는 형식 3을 사용해.

## 14-3. 패키지 이름

```xml
<name>simple_nav</name>
```

패키지 이름을 지정해.

이 이름은 Python 패키지 이름, `setup.py`의 `package_name`, 실행 명령어에서 사용하는 패키지 이름과 일치해야 해.

예를 들어 실행할 때 다음과 같이 사용하지.

```bash
ros2 run simple_nav pub_occupancy_grid
```

## 14-4. 버전과 설명

```xml
<version>0.0.0</version>
<description>Occupancy Grid Publisher in Python for ROS 2 Jazzy</description>
```

- `version`: 패키지 버전
- `description`: 패키지의 기능 설명

`0.0.0`은 초기 실습 패키지에서 사용할 수 있는 버전 값이야.

## 14-5. 관리자와 라이선스

```xml
<maintainer email="user@todo.todo">user</maintainer>
<license>TODO: License declaration</license>
```

패키지를 관리하는 사람과 라이선스를 표시하는 부분이야.

실습에서는 예제 값을 사용할 수 있지만, GitHub에 공개할 프로젝트라면 자신의 정보와 실제 적용할 라이선스로 수정하는 것이 좋아.

## 14-6. 의존성

```xml
<depend>rclpy</depend>
<depend>nav_msgs</depend>
```

이 두 줄은 이번 코드에서 특히 중요해.

### `rclpy`

Python으로 ROS 2 노드와 통신 기능을 작성하는 데 필요해.

### `nav_msgs`

`OccupancyGrid` 메시지를 제공해.

여기서 `<depend>`는 해당 패키지에 필요한 의존성을 선언하는 태그야.

앞서 패키지를 생성할 때 다음 옵션을 사용했지.

```bash
--dependencies rclpy nav_msgs
```

따라서 이 의존성은 일반적으로 생성된 `package.xml`에 이미 기록되어 있어.

## 14-7. 테스트 의존성

```xml
<test_depend>ament_copyright</test_depend>
<test_depend>ament_flake8</test_depend>
<test_depend>ament_pep257</test_depend>
<test_depend>python3-pytest</test_depend>
```

테스트나 코드 품질 검사에 필요한 패키지들이야.

예를 들어 `pytest`는 Python 코드를 테스트할 때 사용해.

이번 실습의 기본 노드를 실행하는 데 반드시 직접 호출해야 하는 부분은 아니지만, 패키지를 검증하거나 프로젝트를 관리할 때 유용해.

## 14-8. 빌드 방식 선언

```xml
<export>
  <build_type>ament_python</build_type>
</export>
```

이 패키지가 Python 기반의 `ament_python` 빌드 방식을 사용한다는 것을 나타내.

패키지를 생성할 때 다음 옵션을 지정한 것과 연결돼.

```bash
--build-type ament_python
```

---

# 15. `setup.py` 자세히 이해하기

`setup.py`는 Python 패키지를 설치하고, ROS 2에서 노드를 실행할 수 있도록 설정하는 파일이야.

여기서 가장 중요한 부분은 `entry_points`야.

```python
from setuptools import find_packages, setup

package_name = 'simple_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pub_occupancy_grid = simple_nav.pub_occupancy_grid:main',
        ],
    },
)
```

## 15-1. 라이브러리 불러오기

```python
from setuptools import find_packages, setup
```

Python 패키지를 설치하기 위한 도구를 불러오는 부분이야.

- `setup`: 패키지의 설치 정보를 설정
- `find_packages`: Python 패키지를 찾아 설치 대상에 포함

## 15-2. 패키지 이름 설정

```python
package_name = 'simple_nav'
```

패키지 이름을 변수에 저장해.

이렇게 하면 아래 설정에서 이름을 반복해서 직접 입력하지 않아도 돼.

```python
name=package_name
```

## 15-3. Python 패키지 검색

```python
packages=find_packages(exclude=['test'])
```

설치할 Python 패키지를 검색하는 설정이야.

일반적으로 `simple_nav/__init__.py`가 있는 안쪽 폴더를 Python 패키지로 인식할 수 있어.

따라서 파일은 다음과 같은 구조여야 해.

```text
simple_nav/
├── setup.py
└── simple_nav/
    ├── __init__.py
    └── pub_occupancy_grid.py
```

## 15-4. `data_files`

```python
data_files=[
    (
        'share/ament_index/resource_index/packages',
        ['resource/' + package_name]
    ),
    (
        'share/' + package_name,
        ['package.xml']
    ),
],
```

ROS 2에서 패키지를 찾는 데 필요한 리소스 파일과 `package.xml`을 설치하도록 설정하는 부분이야.

여기서 `resource/simple_nav`는 `ros2 pkg` 같은 도구가 패키지를 찾는 데 사용하는 리소스 파일이야.

이 파일은 패키지를 생성할 때 보통 자동으로 만들어져.

## 15-5. `install_requires`

```python
install_requires=['setuptools']
```

Python 패키지를 설치할 때 필요한 기본 설치 도구를 지정해.

ROS 2 패키지의 시스템 의존성은 `package.xml`에도 별도로 선언한다는 점을 기억해 둬.

## 15-6. `entry_points`: 가장 중요한 부분

```python
entry_points={
    'console_scripts': [
        'pub_occupancy_grid = simple_nav.pub_occupancy_grid:main',
    ],
},
```

이 설정은 Python 함수를 ROS 2에서 실행할 수 있는 명령어로 등록해.

문자열을 세 부분으로 나눠 보자.

```text
pub_occupancy_grid = simple_nav.pub_occupancy_grid:main
       ①                       ②          ③
```

| 부분 | 의미 |
|---|---|
| `pub_occupancy_grid` | 터미널에서 실행할 명령 이름 |
| `simple_nav.pub_occupancy_grid` | Python 모듈의 위치 |
| `main` | 실행할 함수 이름 |

즉, 다음 명령을 실행하면,

```bash
ros2 run simple_nav pub_occupancy_grid
```

ROS 2가 `simple_nav.pub_occupancy_grid` 모듈을 찾아 그 안의 `main()` 함수를 실행하도록 등록하는 거야.

### 파일 이름과 모듈 이름의 관계

파일 이름이 다음과 같다고 해 보자.

```text
pub_occupancy_grid.py
```

Python에서는 확장자 `.py`를 제외한 이름을 모듈 이름으로 사용해.

따라서 모듈 이름은 다음과 같아.

```text
pub_occupancy_grid
```

그리고 이 파일이 안쪽 `simple_nav` 폴더에 있으므로 모듈의 전체 경로는 다음과 같아.

```text
simple_nav.pub_occupancy_grid
```

파일의 맨 아래에 다음 코드가 있어야 해.

```python
if __name__ == '__main__':
    main()
```

또한 `main()` 함수가 실제로 정의되어 있어야 실행할 수 있어.

---

# 16. 중요한 오류 확인: 4×4 지도와 3×3 지도

네가 올린 코드에는 서로 다른 두 가지 버전이 있어. 이 부분은 꼭 구분해야 해.

### 첫 번째 코드: 실습에서 요구한 4×4 지도

```python
occupancy_grid_msg.info.resolution = 1.0
occupancy_grid_msg.info.width = 4
occupancy_grid_msg.info.height = 4

occupancy_grid_msg.data = [
    100, 0, 0, 0,
    0, -1, 0, 0,
    -1, 0, 100, 0,
    -1, 0, 100, 0
]
```

셀 개수는 다음과 같아.

\[
4 \times 4 = 16
\]

따라서 데이터 16개가 맞아.

### 두 번째 코드: 3×3 지도

```python
occupancy_grid_msg.info.width = 3
occupancy_grid_msg.info.height = 3

occupancy_grid_msg.data = [
    100, 0, 0,
    0, -1, 0,
    0, 0, 100
]
```

셀 개수는 다음과 같아.

\[
3 \times 3 = 9
\]

따라서 데이터 9개가 맞아.

**이번 과제에서는 처음에 제시된 조건대로 `width = 4`, `height = 4`, `data` 16개를 사용하자.** 두 번째 코드의 `3 × 3` 설정을 그대로 사용하면 과제에서 요구한 지도 크기와 달라져.

---

# 17. `setup.cfg`도 확인하기

`ament_python` 패키지를 생성하면 일반적으로 `setup.cfg` 파일도 만들어져.

다음 명령어로 내용을 확인해 봐.

```bash
cd ~/ros2_ws/src/simple_nav
cat setup.cfg
```

일반적으로 다음과 비슷한 설정이 들어 있어.

```ini
[develop]
script_dir=$base/lib/simple_nav

[install]
install_scripts=$base/lib/simple_nav
```

이 설정은 설치된 Python 실행 파일이 ROS 2에서 찾을 수 있는 위치에 배치되도록 도와줘.

패키지를 생성할 때 파일이 이미 만들어져 있다면 그대로 사용하면 돼.

---

# 18. 패키지 빌드하기

이제 작성한 코드를 실제로 빌드하고 실행해 보자.

## 18-1. 파일이 올바른 위치에 있는지 확인

먼저 다음 명령어를 입력해.

```bash
cd ~/ros2_ws
ls src/simple_nav/simple_nav
```

출력에 다음 파일들이 있어야 해.

```text
__init__.py
pub_occupancy_grid.py
```

`setup.py`도 확인해 보자.

```bash
cat src/simple_nav/setup.py
```

특히 아래 부분이 정확해야 해.

```python
entry_points={
    'console_scripts': [
        'pub_occupancy_grid = simple_nav.pub_occupancy_grid:main',
    ],
},
```

## 18-2. ROS 2 환경 설정

```bash
source /opt/ros/jazzy/setup.bash
```

이 명령어는 ROS 2 Jazzy의 실행 환경을 현재 터미널에 설정해.

## 18-3. 빌드 실행

```bash
cd ~/ros2_ws
colcon build --packages-select simple_nav
```

각 부분의 의미는 다음과 같아.

- `colcon build`: 워크스페이스의 패키지를 빌드
- `--packages-select simple_nav`: `simple_nav` 패키지만 빌드

`ament_python`은 Python 패키지이므로 C++처럼 소스 코드를 컴파일하는 방식과는 다르지만, ROS 2에서 사용할 수 있도록 패키지를 설치하고 실행 환경을 구성하는 빌드 과정이 필요해.

성공하면 다음과 비슷한 메시지가 나올 수 있어.

```text
Starting >>> simple_nav
Finished <<< simple_nav
Summary: 1 package finished
```

오류가 발생하면 오류 메시지 전체를 확인해야 해.

## 18-4. 빌드 결과 적용

```bash
source install/setup.bash
```

이 명령어는 현재 워크스페이스에 설치된 패키지를 찾을 수 있도록 환경을 설정해.

여기서 주의할 점이 있어.

```bash
source /opt/ros/jazzy/setup.bash
```

위 명령어는 ROS 2 Jazzy 기본 환경을 설정하고,

```bash
source install/setup.bash
```

위 명령어는 현재 워크스페이스의 패키지를 추가로 사용할 수 있도록 설정해.

일반적으로 새 터미널을 열었을 때는 필요한 환경을 다시 설정해야 해.

## 18-5. 실행 가능한 노드 확인

```bash
ros2 pkg executables simple_nav
```

정상적으로 등록되었다면 다음과 비슷한 결과가 나와.

```text
simple_nav pub_occupancy_grid
```

이 명령어가 출력되지 않는다면 다음 사항을 확인해 봐.

1. `setup.py`의 `entry_points`가 정확한가?
2. Python 파일이 `simple_nav/simple_nav/` 안에 있는가?
3. 파일 이름이 `pub_occupancy_grid.py`인가?
4. 빌드가 성공했는가?
5. `source install/setup.bash`를 실행했는가?

---

# 19. 노드 실행하고 토픽 확인하기

## 19-1. 첫 번째 터미널: 노드 실행

다음 명령어를 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
source install/setup.bash
ros2 run simple_nav pub_occupancy_grid
```

정상적으로 실행되면 다음과 같은 로그가 반복돼.

```text
[INFO] [occupancy_grid_publisher]: Publishing Custom Occupancy Grid...
[INFO] [occupancy_grid_publisher]: Publishing Custom Occupancy Grid...
[INFO] [occupancy_grid_publisher]: Publishing Custom Occupancy Grid...
```

0.5초마다 콜백이 실행되기 때문에 로그도 주기적으로 출력돼.

노드를 종료하려면 해당 터미널에서 `Ctrl+C`를 누르면 돼.

## 19-2. 두 번째 터미널: 토픽 확인

노드를 실행한 상태에서 새 터미널을 열어.

다음 명령어를 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic list
```

목록에서 다음 토픽을 찾아봐.

```text
/custom_occupancy_grid
```

토픽이 보이면 메시지 형식도 확인할 수 있어.

```bash
ros2 topic type /custom_occupancy_grid
```

예상 결과:

```text
nav_msgs/msg/OccupancyGrid
```

메시지가 실제로 발행되는지 확인하려면 다음 명령어를 입력해.

```bash
ros2 topic echo /custom_occupancy_grid
```

그러면 다음과 비슷한 구조의 메시지가 출력돼.

```yaml
header:
  stamp:
    sec: ...
    nanosec: ...
  frame_id: map_frame
info:
  map_load_time:
    sec: 0
    nanosec: 0
  resolution: 1.0
  width: 4
  height: 4
  origin:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
data:
- 100
- 0
- 0
- 0
- 0
- -1
- 0
- 0
- -1
- 0
- 100
- 0
- -1
- 0
- 100
- 0
```

시간값과 출력 형식은 환경에 따라 달라질 수 있어.

**여기서 `width: 4`, `height: 4`, `data`의 값 16개가 확인되면 지도 메시지 설정이 올바르게 적용된 거야.**

---

# 20. RViz2에서 지도 시각화하기

이제 지도 데이터를 눈으로 확인해 보자.

RViz2는 ROS 2에서 센서 데이터, 로봇 모델, 지도, 좌표계 등을 시각화하는 도구야.

이번 실습에서는 RViz2가 발행하는 프로그램이 아니라, 우리가 발행한 지도 데이터를 **구독해서 화면에 표시하는 역할**을 해.

## 20-1. 노드를 먼저 실행

첫 번째 터미널에서 다음 명령어를 실행한 상태로 유지해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
source install/setup.bash
ros2 run simple_nav pub_occupancy_grid
```

## 20-2. RViz2 실행

새 터미널에서 실행해.

```bash
source /opt/ros/jazzy/setup.bash
rviz2
```

RViz2 창이 열릴 때까지 기다려.

## 20-3. Fixed Frame 설정

RViz2 화면 왼쪽의 `Global Options`에서 `Fixed Frame` 항목을 찾아.

기본값이 `map` 등으로 설정되어 있을 수 있어.

이번 메시지에서는 다음과 같이 설정했지.

```python
occupancy_grid_msg.header.frame_id = 'map_frame'
```

따라서 `Fixed Frame`을 다음과 같이 변경해.

```text
map_frame
```

**중요:** `map_frame`을 입력했는데 오류가 발생한다면, 실제로 발행되는 메시지의 `frame_id`부터 확인해 봐. RViz2의 고정 프레임 이름과 메시지의 프레임 이름이 일치해야 해.

## 20-4. Map 디스플레이 추가

RViz2 왼쪽 아래의 `Add` 버튼을 눌러.

일반적으로 다음 경로에서 Map 디스플레이를 선택할 수 있어.

```text
By display type → Map
```

추가한 Map 디스플레이의 속성에서 `Topic` 항목을 찾아 다음 토픽을 선택하거나 입력해.

```text
/custom_occupancy_grid
```

메시지 타입은 다음과 같아야 해.

```text
nav_msgs/msg/OccupancyGrid
```

이제 설정이 올바르다면 지도가 화면에 표시될 수 있어.

### 지도가 보이지 않는 경우

다음 순서로 확인해 봐.

1. 노드가 실행 중인가?
2. `ros2 topic list`에 `/custom_occupancy_grid`가 보이는가?
3. `ros2 topic echo /custom_occupancy_grid`에서 메시지가 출력되는가?
4. RViz2의 `Fixed Frame`이 `map_frame`인가?
5. Map 디스플레이의 토픽이 `/custom_occupancy_grid`인가?
6. Map 디스플레이의 `Status`에 오류가 표시되는가?

참고로 `image.png`는 메시지에 포함된 것이 아니라, 네가 RViz2 화면을 캡처해서 공유하면 그 화면을 보고 설정 오류를 확인할 수 있어.

---

# 21. 자주 발생하는 오류와 해결 방법

### 오류 1. `colcon: command not found`

빌드 도구가 설치되지 않았을 가능성이 있어.

Ubuntu 24.04에서 ROS 2 Jazzy 환경을 사용하고 있다면 다음 명령어로 설치할 수 있어.

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions
```

설치 후 확인해 봐.

```bash
colcon --version
```

### 오류 2. `Package 'simple_nav' not found`

패키지 환경을 적용하지 않았거나 빌드가 제대로 되지 않았을 수 있어.

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select simple_nav
source install/setup.bash
```

### 오류 3. `No executable found`

`setup.py`의 실행 명령 등록을 확인해.

```python
entry_points={
    'console_scripts': [
        'pub_occupancy_grid = simple_nav.pub_occupancy_grid:main',
    ],
},
```

그다음 다시 빌드해.

```bash
cd ~/ros2_ws
colcon build --packages-select simple_nav
source install/setup.bash
ros2 pkg executables simple_nav
```

### 오류 4. RViz2에서 `Fixed Frame [map_frame] does not exist`

메시지의 프레임 이름과 RViz2의 고정 프레임 설정이 일치하지 않을 때 발생할 수 있어.

이번 코드에서는 다음 값을 사용하고 있어.

```python
occupancy_grid_msg.header.frame_id = 'map_frame'
```

따라서 RViz2의 `Fixed Frame`도 `map_frame`으로 설정해 봐.

단, 실제 로봇 시스템에서 사용하는 `map`, `odom`, `base_link` 등의 좌표계는 TF 설정과 함께 관리해야 해.

### 오류 5. `data`와 지도 크기가 맞지 않음

다음 두 값이 중요해.

```python
occupancy_grid_msg.info.width = 4
occupancy_grid_msg.info.height = 4
```

이 경우 `data` 배열의 길이는 반드시 16이어야 해.

```python
len(occupancy_grid_msg.data) == 16
```

코드에서 직접 확인하려면 다음을 사용할 수 있어.

```python
print(len(occupancy_grid_msg.data))
```

---

# 22. 이번 실습에서 반드시 이해해야 할 핵심

이번 코드는 단순히 지도를 화면에 표시하는 실습이 아니라, ROS 2의 메시지 구조와 Publisher의 동작을 이해하는 실습이야.

| 코드 | 핵심 개념 |
|---|---|
| `class OccupancyGridPublisher(Node)` | ROS 2 노드 클래스 |
| `create_publisher()` | Publisher 생성 |
| `create_timer()` | 주기적으로 콜백 실행 |
| `OccupancyGrid()` | 지도 메시지 생성 |
| `header.stamp` | 메시지 시간 정보 |
| `header.frame_id` | 메시지의 기준 좌표계 |
| `info.resolution` | 셀 하나의 실제 크기 |
| `info.width` | 지도 가로 셀 개수 |
| `info.height` | 지도 세로 셀 개수 |
| `info.origin` | 지도 원점의 위치와 방향 |
| `data` | 셀별 점유 정보 |
| `publish()` | 메시지 발행 |
| `rclpy.spin()` | 콜백 처리 및 노드 실행 유지 |
| `entry_points` | Python 함수를 ROS 2 실행 명령으로 등록 |

## 다음 단계: 직접 수정해 보기

코드가 정상적으로 실행되면 다음 세 가지 실습을 추천해.

**실습 1. 지도 해상도 변경하기**

```python
occupancy_grid_msg.info.resolution = 0.5
```

`width`와 `height`는 그대로 두고 해상도만 변경하면 실제 지도 크기가 어떻게 달라지는지 확인할 수 있어.

**실습 2. 지도 크기 변경하기**

```python
occupancy_grid_msg.info.width = 5
occupancy_grid_msg.info.height = 5
```

이때는 셀이 25개이므로 `data` 배열도 25개로 변경해야 해.

**실습 3. 장애물 위치 바꾸기**

```python
occupancy_grid_msg.data = [
    100, 100, 0, 0,
    0, 0, -1, 0,
    0, 100, 100, 0,
    0, 0, 0, 0
]
```

