
# 1. 전체 코드 살펴보기

```python
"""turtlesim과 직진 Publisher를 함께 실행합니다."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # turtlesim turtlesim_node

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen'
    )

    # cmd_vel publisher

    cmd_vel_publisher_node = Node(
        package='turtle_robot',
        executable='lesson_05_cmd_vel_publisher',
        name='cmd_vel_publisher',
        output='screen'
    )

    return LaunchDescription([
        turtlesim_node,
        cmd_vel_publisher_node
    ])
```

이 코드의 실행 구조는 다음과 같아.

```text
             ROS 2 Launch
                  │
          ┌───────┴────────┐
          ▼                ▼
  turtlesim_node     cmd_vel_publisher
          ▲                │
          │                │
          │                │ Twist 메시지 발행
          │                ▼
          └──── /turtle1/cmd_vel ────┘
                  │
                  ▼
             거북이 직진
```

두 개의 노드가 실행돼.

| 노드 | 역할 |
|---|---|
| `turtlesim` | 거북이 시뮬레이터를 실행하고 속도 명령을 처리함 |
| `cmd_vel_publisher` | 속도 명령 메시지를 발행함 |

핵심은 **Launch 파일이 두 노드를 함께 실행하고, 두 노드가 Topic을 통해 통신한다**는 점이야.

---

# 2. `import` 부분

```python
from launch import LaunchDescription
from launch_ros.actions import Node
```

Python에서 Launch 파일을 작성하는 데 필요한 기능을 가져오는 코드야.

## 2-1. `LaunchDescription`

```python
from launch import LaunchDescription
```

Launch 시스템에 실행할 작업 목록을 전달할 때 사용해.

이번 코드에서는 시뮬레이터와 Publisher를 함께 실행해야 하므로, 두 작업을 하나의 `LaunchDescription`으로 묶어.

```python
return LaunchDescription([
    turtlesim_node,
    cmd_vel_publisher_node
])
```

## 2-2. `Node`

```python
from launch_ros.actions import Node
```

ROS 2 노드를 실행하기 위한 Launch 액션이야.

여기서는 `Node()`를 두 번 사용하고 있어.

```python
turtlesim_node = Node(...)
```

```python
cmd_vel_publisher_node = Node(...)
```

각각 시뮬레이터와 Publisher의 실행 정보를 정의하는 거야.

---

# 3. 첫 번째 노드: turtlesim 실행

```python
turtlesim_node = Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='turtlesim',
    output='screen'
)
```

이 부분은 거북이 시뮬레이터를 실행해.

### ① `package='turtlesim'`

```python
package='turtlesim',
```

실행할 프로그램이 들어 있는 ROS 2 패키지를 지정해.

`package`는 실행 파일의 이름이 아니라 **프로그램이 속한 패키지의 이름**이야.

### ② `executable='turtlesim_node'`

```python
executable='turtlesim_node',
```

실제로 실행할 프로그램을 지정해.

터미널에서 다음 명령어를 입력하는 것과 같은 프로그램이야.

```bash
ros2 run turtlesim turtlesim_node
```

여기서 기억할 것은 다음과 같아.

```text
package     = turtlesim
executable  = turtlesim_node
```

### ③ `name='turtlesim'`

```python
name='turtlesim',
```

실행된 ROS 2 노드의 이름을 지정해.

실행 후 다음 명령어로 확인할 수 있어.

```bash
ros2 node list
```

다른 노드가 실행 중이지 않다면 다음과 비슷한 결과가 나올 거야.

```text
/turtlesim
/cmd_vel_publisher
```

`executable`과 `name`은 서로 다른 개념이야.

- `executable`: 실행할 프로그램
- `name`: ROS 2에서 사용하는 노드 이름

### ④ `output='screen'`

```python
output='screen'
```

노드에서 출력하는 로그나 오류 메시지를 화면에서 확인할 수 있도록 지정해.

프로그램에 문제가 생겼을 때 원인을 찾는 데 도움이 돼.

---

# 4. 두 번째 노드: 직진 Publisher 실행

이제 이번 코드에서 가장 중요한 부분이야.

```python
cmd_vel_publisher_node = Node(
    package='turtle_robot',
    executable='lesson_05_cmd_vel_publisher',
    name='cmd_vel_publisher',
    output='screen'
)
```

이 노드는 네가 학습하고 있는 `turtle_robot` 패키지에 있는 Publisher 프로그램을 실행해.

## 4-1. `package='turtle_robot'`

```python
package='turtle_robot',
```

실행할 프로그램이 `turtle_robot`이라는 ROS 2 패키지에 들어 있다는 뜻이야.

이전에 작업하던 workspace 구조를 예로 들면 다음과 같아.

```text
ros2_ws/
└── src/
    └── turtle_robot/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        └── turtle_robot/
            ├── __init__.py
            └── lesson_05_cmd_vel_publisher.py
```

실제 파일 구조는 네 프로젝트에 따라 다를 수 있지만, ROS 2가 해당 패키지의 실행 프로그램을 찾을 수 있도록 등록되어 있어야 해.

## 4-2. `executable='lesson_05_cmd_vel_publisher'`

```python
executable='lesson_05_cmd_vel_publisher',
```

실행할 프로그램의 이름을 지정해.

이 이름은 Python 파일 이름과 비슷하지만, 반드시 같은 것은 아니야.

예를 들어 `setup.py`에서 다음과 같이 등록했다고 가정해 보자.

```python
entry_points={
    'console_scripts': [
        'lesson_05_cmd_vel_publisher = turtle_robot.lesson_05_cmd_vel_publisher:main',
    ],
},
```

여기서 등호 왼쪽에 있는 이름이 실행 파일 이름이야.

```text
lesson_05_cmd_vel_publisher
```

따라서 다음 명령어로 실행할 수 있어.

```bash
ros2 run turtle_robot lesson_05_cmd_vel_publisher
```

Launch 파일은 이 명령어를 대신 실행해 주는 역할을 해.

**중요:** `setup.py`에 실행 파일이 등록되어 있지 않거나 빌드 및 환경 설정이 제대로 되어 있지 않으면 Launch 실행에 실패할 수 있어.

## 4-3. `name='cmd_vel_publisher'`

```python
name='cmd_vel_publisher',
```

실행할 노드의 ROS 2 이름을 지정해.

여기서는 실행 파일 이름과 노드 이름을 다르게 지정했어.

| 구분 | 이름 |
|---|---|
| 패키지 | `turtle_robot` |
| 실행 파일 | `lesson_05_cmd_vel_publisher` |
| ROS 2 노드 이름 | `cmd_vel_publisher` |

이렇게 지정하면 `ros2 node list`에서 일반적으로 다음과 같은 이름을 확인할 수 있어.

```text
/cmd_vel_publisher
```

## 4-4. `output='screen'`

```python
output='screen'
```

Publisher 노드의 로그와 오류 메시지를 화면에서 확인하도록 설정해.

예를 들어 Publisher 코드에 다음과 같은 로그가 있다면,

```python
self.get_logger().info('Publishing velocity')
```

실행할 때 해당 메시지를 확인할 수 있어.

단, 로그를 출력하는 코드가 실제로 있어야 메시지가 표시돼.

---

# 5. 가장 중요한 개념: Publisher와 Topic

Launch 파일 자체는 거북이의 속도를 계산하거나 메시지를 발행하지 않아.

Launch 파일은 Publisher 프로그램을 실행할 뿐이야.

실제 움직임은 `lesson_05_cmd_vel_publisher` 프로그램 내부 코드가 담당해.

앞서 학습한 Lesson 5 코드처럼 다음과 같은 형태라고 가정해 보자.

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelPublisher(Node):

    def __init__(self):
        super().__init__('lesson_05_cmd_vel_publisher')

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
        msg = Twist()
        msg.linear.x = 1.0
        msg.angular.z = 0.0

        self.publisher.publish(msg)


def main(args=None):
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

위 코드는 동작을 설명하기 위한 예시야. 실제 Lesson 5 파일의 속도 값이나 클래스 이름은 다를 수 있어.

이 코드에서 중요한 부분을 살펴보자.

### ① Publisher 생성

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

이 코드는 Publisher를 생성해.

| 항목 | 값 | 의미 |
|---|---|---|
| 메시지 타입 | `Twist` | 속도 정보 메시지 |
| Topic | `/turtle1/cmd_vel` | 속도 명령을 전달할 경로 |
| Queue depth | `10` | 대기 메시지 큐의 깊이 설정 |

### ② 속도 설정

```python
msg = Twist()
msg.linear.x = 1.0
msg.angular.z = 0.0
```

속도 메시지를 생성하고 값을 설정해.

- `linear.x = 1.0`: 앞으로 이동하도록 설정
- `angular.z = 0.0`: 회전 속도를 0으로 설정

따라서 이 값으로 명령을 계속 보내면 거북이는 직진하게 돼.

### ③ 메시지 발행

```python
self.publisher.publish(msg)
```

설정한 속도 메시지를 Topic으로 발행해.

```text
Publisher
    │
    │ Twist 메시지
    ▼
/turtle1/cmd_vel
    │
    ▼
turtlesim_node
    │
    ▼
거북이 이동
```

### ④ 타이머

```python
self.timer = self.create_timer(
    0.1,
    self.publish_velocity
)
```

이 예시에서는 `0.1`초마다 `publish_velocity()` 함수를 호출해.

따라서 초당 약 10회 속도 명령을 발행하게 돼.

여기서 주의할 점이 있어. **0.1초마다 메시지를 보낸다는 뜻이지, 거북이가 0.1초 동안만 움직인다는 뜻은 아니야.** 시뮬레이터가 새로운 속도 명령을 받으면 그 명령을 바탕으로 움직여.

또한 이 예시에서는 회전 속도를 0으로 설정했기 때문에 거북이가 직진해.

---

# 6. `LaunchDescription`으로 두 노드 실행하기

코드의 마지막 부분을 보자.

```python
return LaunchDescription([
    turtlesim_node,
    cmd_vel_publisher_node
])
```

앞에서 정의한 두 노드를 Launch 시스템에 전달하는 부분이야.

```python
turtlesim_node = Node(...)
```

```python
cmd_vel_publisher_node = Node(...)
```

이 두 작업을 리스트에 담아서 반환해.

```python
LaunchDescription([
    turtlesim_node,
    cmd_vel_publisher_node
])
```

그러면 Launch 시스템이 두 노드를 실행해.

다만 리스트에 적힌 순서대로 첫 번째 노드가 완전히 시작된 다음 두 번째 노드가 실행된다고 보장되는 것은 아니야.

이 실습에서는 두 노드가 서로 통신할 수 있도록 같은 ROS 2 환경에서 실행하는 것이 중요해.

---

# 7. 실제 실행 방법

네 workspace가 `~/ros2_ws`이고 패키지 이름이 `turtle_robot`이라고 가정할게.

Launch 파일 이름을 예를 들어 다음과 같이 저장했다고 하자.

```text
turtlesim_cmd_vel.launch.py
```

## 1단계: ROS 2 환경 설정

```bash
source /opt/ros/jazzy/setup.bash
```

시스템에 설치된 ROS 2 Jazzy 환경을 현재 터미널에 설정해.

## 2단계: workspace로 이동

```bash
cd ~/ros2_ws
```

## 3단계: 빌드

```bash
colcon build --packages-select turtle_robot --symlink-install
```

이 명령은 `turtle_robot` 패키지를 빌드해.

## 4단계: workspace 환경 설정

```bash
source install/setup.bash
```

이 명령을 실행하면 현재 workspace의 패키지를 ROS 2가 찾을 수 있도록 환경이 설정돼.

## 5단계: Launch 실행

```bash
ros2 launch turtle_robot turtlesim_cmd_vel.launch.py
```

실행 파일 이름은 실제로 저장한 Launch 파일 이름과 일치해야 해.

성공하면 다음 두 가지가 실행돼.

1. 거북이 시뮬레이터 창
2. 직진 명령을 발행하는 Publisher 노드

Publisher가 정상적으로 동작하고 `/turtle1/cmd_vel`에 속도 명령을 발행한다면 거북이가 움직일 거야.

**참고:** Launch 파일이 `ros2 launch` 명령어로 실행되려면 패키지의 `setup.py`에서 Launch 파일을 설치하도록 설정해야 해. 이전에 설명한 `data_files` 설정이 있는지 확인해 줘.

---

# 8. 실행 후 직접 확인하기

이 실습은 단순히 거북이를 움직이는 데서 끝나지 않고, ROS 2의 통신 구조를 직접 확인하는 것이 중요해.

## 실습 1: 실행 중인 노드 확인

다른 터미널을 열고 실행해.

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 node list
```

예상 결과:

```text
/cmd_vel_publisher
/turtlesim
```

노드 이름은 코드에서 지정한 이름과 일치해야 해. 다른 노드가 실행 중이라면 추가 항목이 표시될 수 있어.

## 실습 2: Topic 확인

```bash
ros2 topic list
```

실행 중인 환경에 따라 다음 토픽을 확인할 수 있어.

```text
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

## 실습 3: Publisher의 속도 메시지 확인

```bash
ros2 topic echo /turtle1/cmd_vel
```

Publisher가 메시지를 발행하고 있다면 다음과 비슷한 결과가 반복해서 표시돼.

```yaml
linear:
  x: 1.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
```

실제 값은 Publisher 코드에 설정한 속도 값에 따라 달라져.

이 명령어를 통해 **Publisher가 실제로 메시지를 발행하는지** 확인할 수 있어.

종료하려면 `Ctrl+C`를 누르면 돼.

## 실습 4: Topic 정보 확인

```bash
ros2 topic info /turtle1/cmd_vel
```

Publisher와 Subscriber의 연결 정보를 확인할 수 있어.

일반적으로 이 실습에서는 다음과 같은 구조가 나타나야 해.

- Publisher: `cmd_vel_publisher`
- Subscriber: `turtlesim`

노드의 실제 이름과 연결 상태에 따라 출력은 달라질 수 있어.

---

# 9. 자주 발생하는 문제

### 문제 1: `Package 'turtle_robot' not found`

workspace 환경이 설정되어 있는지 확인해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
source install/setup.bash
```

### 문제 2: `executable 'lesson_05_cmd_vel_publisher' not found`

실행 파일이 등록되어 있는지 확인해.

```bash
ros2 pkg executables turtle_robot
```

출력 목록에 다음 이름이 있는지 확인해.

```text
turtle_robot lesson_05_cmd_vel_publisher
```

없다면 `setup.py`의 `console_scripts` 설정과 빌드 결과를 확인해야 해.

### 문제 3: Launch 파일을 찾지 못함

```bash
ros2 launch turtle_robot
```

이 명령어로 패키지에서 사용할 수 있는 Launch 파일 목록을 확인하거나, `setup.py`에서 Launch 파일을 설치하도록 설정했는지 확인해.

### 문제 4: 거북이가 움직이지 않음

다음 명령어를 차례대로 실행해.

```bash
ros2 node list
ros2 topic list
ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/cmd_vel
```

특히 `ros2 topic echo`에서 메시지가 출력되는지 확인하는 것이 중요해.

- 메시지가 나오지 않으면 Publisher 코드, 노드 실행 상태, Topic 이름을 확인해.
- 메시지가 나오는데 거북이가 움직이지 않으면 메시지의 `linear.x`, `angular.z` 값과 시뮬레이터의 연결 상태를 확인해.

---

# 10. 이번 실습에서 반드시 기억할 것

| 개념 | 이번 코드에서의 예 |
|---|---|
| Launch 파일 | 두 노드를 함께 실행하는 파일 |
| Node | `turtlesim`, `cmd_vel_publisher` |
| Package | `turtlesim`, `turtle_robot` |
| Executable | `turtlesim_node`, `lesson_05_cmd_vel_publisher` |
| Publisher | 속도 메시지를 발행하는 노드의 기능 |
| Topic | `/turtle1/cmd_vel` |
| Message type | `geometry_msgs/msg/Twist` |
| Subscriber | 속도 메시지를 받아 처리하는 turtlesim 노드 |

가장 중요한 흐름은 다음과 같아.

**Launch 파일 실행 → 두 노드 실행 → Publisher가 `/turtle1/cmd_vel`로 `Twist` 메시지 발행 → turtlesim이 메시지를 받아 거북이를 움직임.**

