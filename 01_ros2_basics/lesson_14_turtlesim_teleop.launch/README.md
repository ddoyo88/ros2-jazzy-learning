
# 1. 코드 전체 살펴보기

먼저 네 코드를 그대로 보자.

```python
"""turtlesim과 키보드 조종 노드를 함께 실행합니다."""

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

    # teleop turtelsim turtle_teleop_key

    teleop_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='turtle_teleop_key',
        prefix='gnome-terminal --wait --',
        output='screen'
    )

    return LaunchDescription([
        turtlesim_node,
        teleop_node
    ])
```

이 코드는 크게 세 부분으로 나뉘어.

| 부분 | 역할 |
|---|---|
| `import` | Launch 파일 작성에 필요한 기능을 가져옴 |
| `Node()` | 실행할 ROS 2 노드를 각각 정의함 |
| `LaunchDescription()` | 정의한 노드들을 한 번에 실행하도록 구성함 |

실행하면 다음과 같은 구조가 만들어져.

```text
ROS 2 Launch
    │
    ├── turtlesim_node
    │      └── 거북이 시뮬레이터 화면
    │
    └── turtle_teleop_key
           └── 키보드 입력을 받아 이동 명령 발행
                      │
                      ▼
             /turtle1/cmd_vel
                      │
                      ▼
                turtlesim_node
                      │
                      ▼
                 거북이 이동
```

핵심은 **시뮬레이터와 키보드 조종 프로그램이 별도의 노드로 실행되고, 토픽을 통해 통신한다는 것**이야.

---

# 2. 첫 번째 부분: import

```python
from launch import LaunchDescription
from launch_ros.actions import Node
```

Python에서 다른 모듈에 정의된 기능을 가져오는 코드야.

## 2-1. `LaunchDescription`

```python
from launch import LaunchDescription
```

`LaunchDescription`은 Launch 파일에서 실행할 작업들을 묶어서 정의할 때 사용해.

예를 들어 다음 두 프로그램을 동시에 실행하고 싶다고 해 보자.

- 거북이 시뮬레이터
- 키보드 조종 프로그램

각 프로그램을 실행할 작업으로 정의한 뒤, `LaunchDescription`에 넣는 거야.

```python
return LaunchDescription([
    turtlesim_node,
    teleop_node
])
```

여기서 리스트 안에 있는 두 항목이 실행할 작업이야.

비유하면 **실행할 프로그램들을 적어 놓은 작업 목록**이라고 생각하면 돼.

## 2-2. `Node`

```python
from launch_ros.actions import Node
```

`Node`는 ROS 2 노드를 실행하기 위한 Launch 액션이야.

여기서는 두 개의 `Node()`를 사용하고 있어.

```python
turtlesim_node = Node(...)
```

```python
teleop_node = Node(...)
```

첫 번째는 시뮬레이터를 실행하고, 두 번째는 키보드 조종 프로그램을 실행해.

주의할 점은 `Node()`가 노드의 내부 코드를 직접 작성하는 기능은 아니라는 거야. 이미 설치된 ROS 2 패키지에서 실행할 프로그램을 지정하는 역할을 해.

---

# 3. 두 번째 부분: turtlesim 노드 실행

```python
turtlesim_node = Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='turtlesim',
    output='screen'
)
```

이 부분을 하나씩 살펴보자.

## 3-1. `package='turtlesim'`

```python
package='turtlesim',
```

실행할 프로그램이 들어 있는 ROS 2 패키지를 지정해.

ROS 2에서 패키지는 노드, 메시지, 서비스, 설정 파일 등의 관련 기능을 묶어 놓은 단위야.

여기서는 ROS 2의 `turtlesim` 패키지를 사용해.

## 3-2. `executable='turtlesim_node'`

```python
executable='turtlesim_node',
```

해당 패키지에서 실제로 실행할 프로그램을 지정해.

정리하면 다음과 같아.

| 설정 | 값 | 의미 |
|---|---|---|
| `package` | `turtlesim` | 프로그램이 속한 패키지 |
| `executable` | `turtlesim_node` | 실행할 프로그램 |

터미널에서 다음 명령어로 직접 실행했던 것과 같은 프로그램이야.

```bash
ros2 run turtlesim turtlesim_node
```

Launch 파일에서는 이 명령어를 직접 입력하는 대신 `Node()`를 사용해 실행을 정의하는 거지.

## 3-3. `name='turtlesim'`

```python
name='turtlesim',
```

실행할 노드의 이름을 지정해.

여기서 주의할 점이 있어.

- `executable='turtlesim_node'`: 실행할 프로그램의 이름
- `name='turtlesim'`: ROS 2에서 해당 노드에 사용할 이름

둘은 서로 달라도 돼.

실행 후 다음 명령어를 입력해 봐.

```bash
ros2 node list
```

다른 노드가 실행 중이지 않다면 다음과 비슷하게 나타날 수 있어.

```text
/turtlesim
/turtle_teleop_key
```

즉, 프로그램 파일 이름과 ROS 2 노드 이름은 구분해야 해.

## 3-4. `output='screen'`

```python
output='screen'
```

노드의 표준 출력과 표준 오류를 화면에 표시하도록 지정하는 설정이야.

프로그램이 로그나 오류 메시지를 출력하면 터미널에서 확인하기 쉬워져.

여기서는 키보드 조종 노드에 별도의 터미널을 열도록 설정했기 때문에 해당 노드의 출력도 그 터미널에서 확인할 수 있어.

---

# 4. 세 번째 부분: 키보드 조종 노드 실행

```python
teleop_node = Node(
    package='turtlesim',
    executable='turtle_teleop_key',
    name='turtle_teleop_key',
    prefix='gnome-terminal --wait --',
    output='screen'
)
```

이 부분은 키보드 입력을 받아 거북이를 움직이는 노드를 실행해.

## 4-1. `package='turtlesim'`

```python
package='turtlesim',
```

시뮬레이터와 마찬가지로 `turtlesim` 패키지에 들어 있는 프로그램을 사용한다는 뜻이야.

## 4-2. `executable='turtle_teleop_key'`

```python
executable='turtle_teleop_key',
```

키보드로 거북이를 조종하는 실행 프로그램을 지정해.

터미널에서 직접 실행한다면 다음과 같아.

```bash
ros2 run turtlesim turtle_teleop_key
```

이 프로그램은 키보드 입력을 받아 거북이의 이동 속도를 나타내는 메시지를 발행해.

일반적으로 다음 토픽을 사용해.

```text
/turtle1/cmd_vel
```

메시지 타입은 다음과 같아.

```text
geometry_msgs/msg/Twist
```

`Twist` 메시지에는 선속도와 각속도가 들어 있어.

대표적으로 사용하는 필드는 다음과 같아.

| 필드 | 의미 |
|---|---|
| `linear.x` | 앞뒤 방향 속도 |
| `angular.z` | 평면에서 회전하는 속도 |

예를 들어 `linear.x`가 양수이면 앞으로 움직이고, `angular.z`의 값에 따라 회전해.

키보드 조종 노드가 메시지를 발행하면 시뮬레이터 노드가 그 메시지를 받아 거북이를 움직이는 구조야.

## 4-3. `name='turtle_teleop_key'`

```python
name='turtle_teleop_key',
```

키보드 조종 노드의 ROS 2 이름을 지정해.

따라서 노드 목록을 확인하면 `/turtle_teleop_key`와 같은 이름이 나타날 수 있어.

이 이름도 실행 파일 이름과 반드시 같아야 하는 것은 아니야.

---

# 5. 가장 중요한 부분: `prefix='gnome-terminal --wait --'`

```python
prefix='gnome-terminal --wait --',
```

이 설정은 **키보드 조종 프로그램을 별도의 GNOME 터미널 창에서 실행하기 위한 것**이야.

왜 별도 터미널이 필요할까?

키보드 조종 프로그램은 키보드 입력을 직접 받아야 하기 때문이야.

Launch 파일에서 프로그램을 실행하더라도, 키보드 입력을 받을 터미널이 제대로 연결되어 있지 않으면 조종이 불편하거나 키 입력이 제대로 전달되지 않을 수 있어.

각 요소를 살펴보자.

| 요소 | 의미 |
|---|---|
| `gnome-terminal` | Ubuntu의 GNOME 터미널을 실행 |
| `--wait` | 해당 터미널에서 실행한 명령이 끝날 때까지 기다림 |
| `--` | 터미널에 전달할 명령의 시작을 구분 |

따라서 Launch 시스템이 키보드 조종 노드를 실행할 때 별도의 터미널 창을 열도록 하는 거야.

### 실행 후 어떻게 될까?

1. Launch 파일이 실행된다.
2. 거북이 시뮬레이터 창이 열린다.
3. 키보드 조종용 터미널 창이 열린다.
4. 키보드 조종 터미널을 클릭해 활성화한다.
5. 지원되는 방향키를 눌러 거북이를 움직인다.

**중요:** 이 설정은 Ubuntu의 GNOME 데스크톱 환경을 전제로 해. GNOME Terminal이 설치되어 있지 않거나 다른 데스크톱 환경을 사용한다면 실행되지 않을 수 있어.

또한 `--wait`는 키보드 입력을 가능하게 만드는 옵션 자체가 아니야. 터미널 프로세스의 실행과 종료를 관리하는 옵션이야.

---

# 6. 마지막 부분: `LaunchDescription`

```python
return LaunchDescription([
    turtlesim_node,
    teleop_node
])
```

이 부분이 Launch 파일의 핵심이야.

앞에서 두 가지 실행 작업을 정의했지?

```python
turtlesim_node = Node(...)
```

```python
teleop_node = Node(...)
```

그런데 작업을 정의하는 것만으로는 Launch 파일이 어떤 작업을 실행해야 하는지 전달되지 않아.

그래서 다음과 같이 실행할 작업들을 `LaunchDescription`에 넣어 반환하는 거야.

```python
return LaunchDescription([
    turtlesim_node,
    teleop_node
])
```

여기서 `return`은 `generate_launch_description()` 함수가 생성한 Launch 설명을 반환한다는 뜻이야.

Launch 시스템은 이 설명을 읽고 정의된 노드들을 실행해.

### 꼭 기억할 점

리스트의 순서대로 노드를 적었다고 해서 모든 노드가 반드시 앞의 노드가 완전히 실행된 뒤에만 시작되는 것은 아니야.

이 코드는 두 노드를 모두 실행 대상으로 등록하는 구조야.

---

# 7. 실제로 실행하는 방법

이 Launch 파일을 예를 들어 `turtlesim_teleop.launch.py`라는 이름으로 저장했다고 해 보자.

ROS 2 Python 패키지 안에서 Launch 파일을 관리하는 일반적인 구조는 다음과 같아.

```text
ros2_ws/
└── src/
    └── turtle_robot/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── turtle_robot/
        └── launch/
            └── turtlesim_teleop.launch.py
```

단, 패키지에 따라 `launch` 폴더 위치와 설치 설정은 달라질 수 있어.

## 1단계. Launch 파일 설치 설정 확인

Python 패키지의 `setup.py`에 Launch 파일을 설치하는 설정이 있어야 해.

일반적인 예시는 다음과 같아.

```python
import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'turtle_robot'

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
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='ROS 2 learning package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
```

이미 `setup.py`가 있다면 전체 내용을 무작정 덮어쓰지 말고, `data_files`에 Launch 파일 설치 설정이 있는지 확인해.

## 2단계. 빌드

터미널에서 실행해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
```

빌드가 성공하면 다음을 실행해.

```bash
source install/setup.bash
```

## 3단계. Launch 파일 실행

```bash
ros2 launch turtle_robot turtlesim_teleop.launch.py
```

이제 시뮬레이터와 키보드 조종 프로그램이 실행되어야 해.

종료하려면 Launch를 실행한 터미널에서 `Ctrl+C`를 누르면 돼. 별도 터미널에 실행된 프로세스는 환경에 따라 별도로 종료해야 할 수도 있어.

---

# 8. 실행이 안 될 때 확인할 것

### 문제 1: `Package 'turtle_robot' not found`

workspace 환경을 source했는지 확인해.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
source install/setup.bash
```

### 문제 2: `executable 'turtle_teleop_key' not found`

먼저 실행 파일이 설치되어 있는지 확인해.

```bash
ros2 pkg executables turtlesim
```

출력에 `turtle_teleop_key`가 있는지 확인해.

### 문제 3: GNOME 터미널이 열리지 않음

다음 명령어로 GNOME Terminal이 설치되어 있는지 확인해.

```bash
which gnome-terminal
```

아무 경로도 나오지 않는다면 설치 여부를 확인해야 해.

### 문제 4: 키보드를 눌러도 거북이가 움직이지 않음

다음을 확인해.

1. 키보드 조종용 터미널 창을 클릭해 활성화했는가?
2. `turtle_teleop_key` 프로세스가 실행 중인가?
3. `/turtle1/cmd_vel` 토픽이 존재하는가?
4. 다른 노드가 동시에 속도 명령을 발행하고 있지는 않은가?

확인 명령어:

```bash
ros2 node list
ros2 topic list
ros2 topic info /turtle1/cmd_vel
```

---

# 9. 실습으로 직접 확인하기

실행한 뒤 별도의 터미널에서 다음 명령어를 입력해 봐.

### 노드 목록

```bash
ros2 node list
```

**질문:** 시뮬레이터 노드와 키보드 조종 노드가 각각 어떤 이름으로 표시되는가?

### 토픽 목록

```bash
ros2 topic list
```

**질문:** 거북이의 속도 명령을 전달하는 토픽 이름은 무엇인가?

정답:

```text
/turtle1/cmd_vel
```

### 메시지 타입 확인

```bash
ros2 topic type /turtle1/cmd_vel
```

정답:

```text
geometry_msgs/msg/Twist
```

### 실제 메시지 확인

```bash
ros2 topic echo /turtle1/cmd_vel
```

키보드 조종 터미널에서 방향키를 누르면 속도 메시지가 출력되는 것을 확인할 수 있어. 종료하려면 `Ctrl+C`를 눌러.

---

# 10. 최종 핵심 정리

이 코드에서 가장 중요한 다섯 가지는 다음과 같아.

1. **`Node()`**: 실행할 ROS 2 프로그램을 정의한다.
2. **`package`**: 실행 프로그램이 속한 패키지를 지정한다.
3. **`executable`**: 실제로 실행할 프로그램을 지정한다.
4. **`prefix`**: 프로그램을 실행하는 명령 앞에 추가할 명령을 지정한다. 여기서는 별도 GNOME 터미널을 연다.
5. **`LaunchDescription()`**: 실행할 작업들을 묶어 Launch 시스템에 전달한다.

그리고 전체 동작은 이렇게 기억하면 돼.

