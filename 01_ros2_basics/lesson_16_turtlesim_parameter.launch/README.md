
# 1. 전체 실행 구조 이해하기

먼저 코드가 실행되는 흐름을 그림으로 보면 다음과 같아.

```text
                  ROS 2 Launch
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
      turtlesim_node        parameter_node
            ▲                     │
            │                     │
            │             cmd_vel.yaml
            │                     │
            │              속도 파라미터
            │                     │
            │                     ▼
            │             Twist 메시지 발행
            │                     │
            └──── /turtle1/cmd_vel┘
                       │
                       ▼
                  거북이 이동
```

각 요소의 역할은 다음과 같아.

| 요소 | 역할 |
|---|---|
| `turtlesim_node` | 거북이 시뮬레이터를 실행 |
| `parameter_node` | 속도 파라미터를 사용하는 Publisher 노드를 실행 |
| `cmd_vel.yaml` | Publisher에서 사용할 파라미터 값을 저장 |
| `/turtle1/cmd_vel` | 거북이의 속도 명령을 전달하는 토픽 |

**핵심:** Launch 파일이 YAML 파일의 경로를 찾고, 해당 설정을 Publisher 노드에 전달해 주는 구조야.

다만 거북이가 실제로 어떻게 움직이는지는 `lesson_13_cmd_vel_parameters` 프로그램의 코드에 달려 있어. YAML에 속도 값을 지정했다고 해서 속도가 자동으로 증가하는 것은 아니야.

---

# 2. 첫 번째 부분: `import`

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
```

각각의 역할을 살펴보자.

## 2-1. `import os`

```python
import os
```

Python에서 운영체제와 파일 경로 등을 다룰 수 있도록 `os` 모듈을 가져오는 코드야.

이번 코드에서는 다음 기능을 사용해.

```python
os.path.join(...)
```

여러 경로 요소를 합쳐서 파일 경로를 만드는 기능이야.

예를 들어 다음과 같이 사용할 수 있어.

```python
import os

path = os.path.join(
    '/home/logan',
    'ros2_ws',
    'config',
    'cmd_vel.yaml'
)

print(path)
```

Ubuntu에서는 다음과 같은 경로가 만들어져.

```text
/home/logan/ros2_ws/config/cmd_vel.yaml
```

경로를 문자열로 직접 이어 붙이는 것보다 `os.path.join()`을 사용하면 경로를 다루기 편해.

## 2-2. `get_package_share_directory`

```python
from ament_index_python.packages import get_package_share_directory
```

이 함수는 ROS 2 패키지가 설치된 **share 디렉터리의 경로**를 찾아 줘.

예를 들어 다음 코드를 실행한다고 해 보자.

```python
get_package_share_directory('turtle_robot')
```

정상적으로 패키지를 찾으면 다음과 비슷한 경로를 반환할 수 있어.

```text
/home/logan/ros2_ws/install/turtle_robot/share/turtle_robot
```

실제 경로는 workspace와 설치 환경에 따라 달라질 수 있어.

여기서 중요한 점은 `src` 디렉터리의 경로를 찾는 것이 아니라, 일반적으로 ROS 2 패키지가 설치된 `share` 디렉터리의 경로를 찾는다는 거야.

왜 설치 경로를 사용할까?

Launch 파일을 실행할 때 패키지의 파일을 안정적으로 찾기 위해서야. 특히 `ros2 launch`로 실행할 때는 패키지 설치 설정이 올바르게 되어 있어야 해.

## 2-3. `LaunchDescription`과 `Node`

```python
from launch import LaunchDescription
from launch_ros.actions import Node
```

앞에서 배운 내용이므로 간단히 정리할게.

- `LaunchDescription`: 함께 실행할 작업들을 묶어서 Launch 시스템에 전달해.
- `Node`: 실행할 ROS 2 노드를 정의해.

이번에는 두 개의 노드를 실행해.

```python
turtlesim_node = Node(...)
```

```python
parameter_node = Node(...)
```

첫 번째는 시뮬레이터이고, 두 번째는 파라미터를 사용하는 Publisher야.

---

# 3. 핵심 코드: YAML 파일 경로 만들기

이 부분이 이번 코드에서 가장 중요해.

```python
def generate_launch_description():
    config_file_path = os.path.join(
        get_package_share_directory('turtle_robot'),
        'config',
        'cmd_vel.yaml'
    )
```

한 줄씩 살펴보자.

### ① `generate_launch_description()`

```python
def generate_launch_description():
```

ROS 2 Launch 시스템이 실행할 작업을 정의하는 함수야.

Launch 시스템은 이 함수가 반환하는 `LaunchDescription`을 이용해 노드들을 실행해.

### ② `get_package_share_directory('turtle_robot')`

```python
get_package_share_directory('turtle_robot')
```

`turtle_robot` 패키지가 설치된 share 디렉터리를 찾아.

예를 들어 반환된 경로가 다음과 같다고 가정해 보자.

```text
/home/logan/ros2_ws/install/turtle_robot/share/turtle_robot
```

### ③ `'config'`

```python
'config',
```

패키지의 share 디렉터리 안에 있는 `config` 폴더를 지정해.

일반적으로 설정 파일을 관리할 때 `config`라는 폴더 이름을 사용해.

### ④ `'cmd_vel.yaml'`

```python
'cmd_vel.yaml'
```

실제로 사용할 YAML 설정 파일의 이름이야.

### ⑤ `os.path.join()`으로 경로 합치기

```python
config_file_path = os.path.join(
    get_package_share_directory('turtle_robot'),
    'config',
    'cmd_vel.yaml'
)
```

위 세 가지 경로 요소를 합치면 다음과 같은 경로가 만들어져.

```text
/home/logan/ros2_ws/install/turtle_robot/share/turtle_robot/config/cmd_vel.yaml
```

이것은 경로의 예시야. 네 컴퓨터에서 정확한 경로를 확인하려면 다음 명령어를 사용하면 돼.

```bash
ros2 pkg prefix turtle_robot
```

예를 들어 다음 경로가 출력됐다면,

```text
/home/logan/ros2_ws/install/turtle_robot
```

패키지의 share 디렉터리는 일반적으로 다음과 같아.

```text
/home/logan/ros2_ws/install/turtle_robot/share/turtle_robot
```

**주의:** `src/turtle_robot/config/cmd_vel.yaml`에 파일을 만들어 놓았다고 해서 설치 경로에도 자동으로 복사되는 것은 아니야. `setup.py`에서 YAML 파일을 설치하도록 설정해야 해. 이 부분은 뒤에서 설명할게.

---

# 4. 첫 번째 노드: turtlesim 실행

```python
turtlesim_node = Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='turtlesim',
    output='screen'
)
```

이 부분은 이전 Launch 파일과 동일해.

| 설정 | 의미 |
|---|---|
| `package='turtlesim'` | `turtlesim` 패키지를 사용 |
| `executable='turtlesim_node'` | 시뮬레이터 프로그램을 실행 |
| `name='turtlesim'` | 노드 이름을 `turtlesim`으로 지정 |
| `output='screen'` | 로그를 화면에 표시 |

터미널에서 다음 명령어로 실행하는 것과 같은 프로그램이야.

```bash
ros2 run turtlesim turtlesim_node
```

Launch 파일에서는 시뮬레이터와 Publisher를 함께 실행하기 위해 `Node()`를 사용한 거야.

---

# 5. 두 번째 노드: Parameter Publisher 실행

이번 코드의 핵심 부분이야.

```python
parameter_node = Node(
    package='turtle_robot',
    executable='lesson_13_cmd_vel_parameters',
    parameters=[config_file_path],
    output='screen',
)
```

여기서는 세 가지를 이해해야 해.

## 5-1. `package='turtle_robot'`

```python
package='turtle_robot',
```

실행할 프로그램이 `turtle_robot` 패키지에 들어 있다는 뜻이야.

## 5-2. `executable='lesson_13_cmd_vel_parameters'`

```python
executable='lesson_13_cmd_vel_parameters',
```

실행할 프로그램의 이름을 지정해.

앞에서 작성한 Lesson 13 Publisher를 실행하는 거야.

터미널에서 직접 실행한다면 다음과 같아.

```bash
ros2 run turtle_robot lesson_13_cmd_vel_parameters
```

단, 이 명령어가 동작하려면 해당 실행 파일이 `setup.py`에 등록되어 있어야 해.

## 5-3. 가장 중요한 부분: `parameters=[config_file_path]`

```python
parameters=[config_file_path],
```

이 설정은 ROS 2 노드를 실행할 때 YAML 파일에 정의된 파라미터를 전달해.

예를 들어 YAML 파일에 다음과 같이 적혀 있다고 가정해 보자.

```yaml
lesson_13_cmd_vel_parameters:
  ros__parameters:
    linear_speed: 1.0
    angular_speed: 1.0
```

그러면 Launch 시스템은 해당 YAML 설정을 `lesson_13_cmd_vel_parameters`라는 노드에 적용해.

이때 중요한 것은 **YAML의 노드 이름과 실제 실행되는 ROS 2 노드 이름이 일치해야 한다는 점**이야.

현재 Launch 코드의 `parameter_node`에는 `name`이 지정되어 있지 않아. 따라서 ROS 2 노드의 기본 이름이 실행 파일이나 프로그램 내부 설정에 따라 결정될 수 있어.

앞에서 설명한 Lesson 13 코드가 다음과 같이 작성되어 있다면,

```python
super().__init__('lesson_13_cmd_vel_parameters')
```

노드 이름은 다음과 같아.

```text
/lesson_13_cmd_vel_parameters
```

따라서 위 YAML 파일이 해당 노드에 적용될 수 있어.

하지만 노드 이름이 다르면 YAML 설정이 적용되지 않을 수 있으므로, **Launch 파일에서 노드 이름을 명시적으로 지정하는 것을 추천해.**

예를 들면 다음과 같아.

```python
parameter_node = Node(
    package='turtle_robot',
    executable='lesson_13_cmd_vel_parameters',
    name='lesson_13_cmd_vel_parameters',
    parameters=[config_file_path],
    output='screen',
)
```

이렇게 하면 YAML 파일에서 지정할 노드 이름을 명확하게 맞출 수 있어.

---

# 6. `cmd_vel.yaml` 파일은 어떻게 작성할까?

일반적인 ROS 2 파라미터 YAML 파일은 다음 구조를 사용해.

```yaml
노드이름:
  ros__parameters:
    파라미터이름: 값
```

이번 실습에서는 다음과 같이 작성할 수 있어.

```yaml
lesson_13_cmd_vel_parameters:
  ros__parameters:
    linear_speed: 1.0
    angular_speed: 1.0
```

각 항목의 의미는 다음과 같아.

| YAML 항목 | 의미 |
|---|---|
| `lesson_13_cmd_vel_parameters` | 파라미터를 적용할 노드 이름 |
| `ros__parameters` | ROS 2 파라미터 설정을 나타내는 예약된 키 |
| `linear_speed` | 직선 방향 속도 파라미터 |
| `angular_speed` | 회전 속도 파라미터 |

여기서 `linear_speed`와 `angular_speed`는 Lesson 13 Python 코드에서 선언한 이름과 같아야 해.

예를 들어 Python 코드에 다음과 같이 작성되어 있다면,

```python
self.declare_parameter('linear_speed', 1.0)
self.declare_parameter('angular_speed', 1.0)
```

YAML에서도 동일한 이름을 사용해야 해.

```yaml
linear_speed: 1.0
angular_speed: 1.0
```

이름이 다르면 원하는 파라미터를 설정할 수 없어.

### 속도 값을 변경하려면?

예를 들어 직선 속도를 높이고 회전 속도를 낮추고 싶다면 다음처럼 설정할 수 있어.

```yaml
lesson_13_cmd_vel_parameters:
  ros__parameters:
    linear_speed: 2.0
    angular_speed: 0.5
```

이 값은 Publisher 코드가 해당 파라미터를 읽어 속도 메시지에 반영하도록 작성되어 있을 때 실제 움직임에 영향을 줘.

**주의:** `linear_speed`를 `2.0`으로 설정한다고 해서 속도가 점점 증가하는 것은 아니야. 이는 기본적으로 파라미터에 지정된 값이야. 점진적으로 속도를 높이려면 Python 코드에 별도의 증가 로직이 필요해.

---

# 7. YAML 파일을 설치 경로에 복사하기

Launch 파일이 `get_package_share_directory()`를 사용하므로, YAML 파일을 패키지의 설치 경로에서 찾을 수 있어야 해.

네가 사용하는 `turtle_robot`이 Python 패키지라면 `setup.py`에 다음과 같은 설정이 필요해.

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
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
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
        'console_scripts': [
            'lesson_13_cmd_vel_parameters = turtle_robot.lesson_13_cmd_vel_parameters:main',
        ],
    },
)
```

위 코드는 구조를 보여 주는 예시야. 네 `setup.py`에 이미 다른 실행 파일들이 등록되어 있다면 기존 내용을 유지하고 필요한 설정만 추가해야 해.

특히 아래 두 부분을 확인해 줘.

**Launch 파일 설치 설정**

```python
(
    os.path.join('share', package_name, 'launch'),
    glob('launch/*.launch.py')
),
```

**YAML 파일 설치 설정**

```python
(
    os.path.join('share', package_name, 'config'),
    glob('config/*.yaml')
),
```

YAML 파일은 다음 위치에 있다고 가정했어.

```text
~/ros2_ws/src/turtle_robot/config/cmd_vel.yaml
```

폴더 구조는 다음과 같아야 해.

```text
turtle_robot/
├── package.xml
├── setup.py
├── launch/
│   └── turtlesim_parameters.launch.py
├── config/
│   └── cmd_vel.yaml
└── turtle_robot/
    └── lesson_13_cmd_vel_parameters.py
```

---

# 8. 실제 실행 순서

이제 실제 Ubuntu 터미널에서 실행해 보자.

### 1단계: ROS 2 환경 설정

```bash
source /opt/ros/jazzy/setup.bash
```

### 2단계: workspace로 이동

```bash
cd ~/ros2_ws
```

### 3단계: 패키지 빌드

```bash
colcon build --packages-select turtle_robot --symlink-install
```

### 4단계: workspace 환경 설정

```bash
source install/setup.bash
```

### 5단계: Launch 실행

Launch 파일 이름이 `turtlesim_parameters.launch.py`라면 다음과 같이 실행해.

```bash
ros2 launch turtle_robot turtlesim_parameters.launch.py
```

실행 파일 이름은 실제로 저장한 파일 이름과 일치해야 해.

정상적으로 실행되면 다음 두 노드가 동작해야 해.

- `turtlesim`: 거북이 시뮬레이터
- `lesson_13_cmd_vel_parameters`: 속도 파라미터를 사용하는 Publisher

---

# 9. 파라미터가 적용되었는지 확인하기

Launch 실행 후 **새 터미널을 열어** 다음 명령어를 실행해 봐.

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

### ① 실행 중인 노드 확인

```bash
ros2 node list
```

예상 결과는 다음과 비슷해.

```text
/lesson_13_cmd_vel_parameters
/turtlesim
```

### ② 파라미터 목록 확인

```bash
ros2 param list /lesson_13_cmd_vel_parameters
```

`linear_speed`, `angular_speed`가 목록에 있는지 확인해.

### ③ 파라미터 값 확인

```bash
ros2 param get /lesson_13_cmd_vel_parameters linear_speed
```

예상 결과:

```text
Double value is: 1.0
```

회전 속도도 확인해.

```bash
ros2 param get /lesson_13_cmd_vel_parameters angular_speed
```

예상 결과:

```text
Double value is: 1.0
```

YAML 파일에 다른 값을 입력했다면 그 값이 표시되어야 해.

### ④ 실행 중에 파라미터 변경하기

다음 명령어를 실행하면 실행 중인 노드의 파라미터를 변경할 수 있어.

```bash
ros2 param set /lesson_13_cmd_vel_parameters linear_speed 2.0
```

그리고 값을 확인해.

```bash
ros2 param get /lesson_13_cmd_vel_parameters linear_speed
```

다만 **파라미터 값이 변경되었다고 해서 Publisher가 그 값을 자동으로 반영하는 것은 아니야.** Python 코드가 타이머 콜백 등에서 `get_parameter('linear_speed').value`를 읽어 속도 메시지에 반영하도록 작성되어 있어야 해.

---

# 10. 이번 코드에서 꼭 알아야 할 핵심 개념

| 개념 | 설명 |
|---|---|
| Launch 파일 | 여러 ROS 2 노드를 함께 실행하는 파일 |
| `get_package_share_directory()` | 설치된 패키지의 share 디렉터리 경로를 찾는 함수 |
| `os.path.join()` | 여러 경로 요소를 합쳐 파일 경로를 만드는 함수 |
| YAML | 파라미터 설정값을 저장하는 파일 형식 |
| `parameters=[config_file_path]` | YAML 설정을 노드에 전달하는 Launch 설정 |
| `ros__parameters` | ROS 2 YAML에서 파라미터를 정의하는 키 |
| `linear_speed` | 직선 속도를 설정하는 파라미터 |
| `angular_speed` | 회전 속도를 설정하는 파라미터 |

이번 실습의 핵심 흐름은 다음과 같아.

**Launch 파일 실행 → 패키지 설치 경로 확인 → `cmd_vel.yaml` 읽기 → Publisher 노드에 파라미터 전달 → Publisher가 파라미터 값을 사용해 `Twist` 메시지 발행 → turtlesim이 거북이를 움직임.**

