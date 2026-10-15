# ROS 2 Jazzy 필수 Todo 정답 및 실습 기록

> 학습 환경: Ubuntu 24.04 LTS · ROS 2 Jazzy\
> 목적: Linux 기본 명령어, ROS 2 workspace, topic, service의 기본 흐름을
> 직접 실행하고 복습하기

------------------------------------------------------------------------

## 1. Linux 기본 명령어 5개 이상 직접 실행하기

터미널을 열고 아래 명령어를 하나씩 실행한다.

  명령어      기능                                 예시
  ----------- ------------------------------------ ------------------------------------
  `pwd`       현재 작업 디렉터리 출력              `pwd`
  `ls`        현재 디렉터리의 파일·폴더 목록       `ls -la`
  `cd`        디렉터리 이동                        `cd ~/ros2_ws`
  `mkdir`     새 디렉터리 생성                     `mkdir -p ~/practice_folder`
  `touch`     빈 파일 생성                         `touch ~/practice_folder/test.txt`
  `cat`       텍스트 파일 내용 출력                `cat /etc/os-release`
  `cp`        파일 복사                            `cp test.txt test_copy.txt`
  `mv`        파일 이동 또는 이름 변경             `mv test_copy.txt renamed.txt`
  `rm`        파일 삭제                            `rm renamed.txt`
  `ip addr`   네트워크 인터페이스와 IP 주소 확인   `ip addr`

### 직접 실행 확인

다음 명령어를 차례로 실행해 본다.

``` bash
pwd
ls -la
cd ~/ros2_ws
pwd
mkdir -p ~/practice_folder
touch ~/practice_folder/test.txt
ls -l ~/practice_folder
cat /etc/os-release
ip addr
```

**주의:** `rm`은 파일을 삭제한다. 익숙해지기 전에는 중요한 파일에
사용하지 않는다.

------------------------------------------------------------------------

## 2. ROS 2 workspace에서 build와 source 순서 확인하기

ROS 2 패키지 코드를 수정한 뒤에는 보통 **build → source → 실행** 순서로
진행한다.

``` bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select turtle_robot --symlink-install
source install/setup.bash
```

각 명령어의 의미:

1.  `source /opt/ros/jazzy/setup.bash`\
    시스템에 설치된 ROS 2 Jazzy 환경을 현재 터미널에 설정한다.
2.  `cd ~/ros2_ws`\
    ROS 2 workspace 폴더로 이동한다.
3.  `colcon build --packages-select turtle_robot --symlink-install`\
    `turtle_robot` 패키지만 빌드한다. `--symlink-install`은 Python 파일
    등의 개발 중 변경 사항을 확인하기 편하게 해 준다.
4.  `source install/setup.bash`\
    현재 workspace의 패키지를 현재 터미널에서 찾을 수 있도록 환경을
    설정한다.

빌드에 성공했다면 등록한 실행 파일을 다음처럼 실행할 수 있다.

``` bash
ros2 run turtle_robot <실행파일이름>
```

`<실행파일이름>`은 실제 패키지의 `setup.py`에 등록한 console script
이름으로 바꾼다.

### 확인 명령어

``` bash
ros2 pkg list | grep turtle_robot
ros2 pkg executables turtle_robot
```

**기억할 점:** 새 터미널을 열면 ROS 2 환경과 workspace 환경을 다시
`source`해야 할 수 있다. `colcon: command not found`가 나오면 먼저
필요한 빌드 도구가 설치되어 있는지 확인한다.

``` bash
sudo apt update
sudo apt install python3-colcon-common-extensions
```

------------------------------------------------------------------------

## 3. node / topic / publisher / subscriber를 한 문장으로 설명하기

-   **Node(노드):** ROS 2에서 한 가지 역할이나 기능을 수행하는 독립적인
    프로그램 단위이다.
-   **Topic(토픽):** 노드끼리 메시지를 주고받을 때 사용하는 이름이 붙은
    통신 경로이다.
-   **Publisher(퍼블리셔):** 특정 토픽으로 메시지를 발행하는 노드의 통신
    기능이다.
-   **Subscriber(서브스크라이버):** 특정 토픽을 구독하고 새 메시지가
    오면 처리하는 노드의 통신 기능이다.

### 예시

`turtlesim`에서 `/turtle1/cmd_vel` 토픽으로 속도 명령을 보내면 거북이가
움직인다.

-   토픽: `/turtle1/cmd_vel`
-   메시지 타입: `geometry_msgs/msg/Twist`
-   Publisher: `Twist` 메시지를 발행하는 노드
-   Subscriber: 해당 토픽을 구독해 속도 명령을 받는 노드

------------------------------------------------------------------------

## 4. Lesson 3 subscriber 코드에서 topic 이름, message type, callback 찾기

Subscriber 코드를 읽을 때 아래 세 가지를 찾는다.

1.  **Topic 이름:** `create_subscription(...)`의 두 번째 인자
2.  **Message type:** `create_subscription(...)`의 첫 번째 인자
3.  **Callback 함수:** `create_subscription(...)`의 세 번째 인자

예를 들어 다음과 같은 코드라면:

``` python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.pose_callback,
    10
)
```

정답:

  항목            정답
  --------------- ----------------------------------------
  Topic 이름      `/turtle1/pose`
  Message type    `turtlesim/msg/Pose` (`Pose`로 import)
  Callback 함수   `self.pose_callback`
  Queue depth     `10`

`Pose`를 사용하려면 일반적으로 다음 import가 필요하다.

``` python
from turtlesim.msg import Pose
```

Callback 함수는 메시지가 도착했을 때 실행되는 함수다. 예를 들면:

``` python
def pose_callback(self, msg):
    self.get_logger().info(
        f'x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
    )
```

실제 Lesson 3 파일의 토픽 이름이나 callback 함수가 다르면 **코드에 적힌
이름이 정답**이다. 파일에서 `create_subscription`을 찾아 확인한다.

------------------------------------------------------------------------

## 5. `ros2 topic list`와 `ros2 topic echo` 실행하기

### 5-1. turtlesim 실행

터미널 1:

``` bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

터미널 2:

``` bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

출력 목록에는 실행 중인 노드에 따라 다음과 같은 토픽이 나타날 수 있다.

``` text
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
```

실제로 표시되는 목록은 실행 환경에 따라 다를 수 있다.

### 5-2. 토픽 메시지 확인

거북이 위치를 계속 출력한다.

``` bash
ros2 topic echo /turtle1/pose
```

출력 예시:

``` yaml
x: 5.5
y: 5.5
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

숫자는 거북이의 현재 상태에 따라 달라진다. 종료하려면 `Ctrl+C`를 누른다.

### 5-3. 토픽의 메시지 타입 확인

``` bash
ros2 topic type /turtle1/pose
```

예상 결과:

``` text
turtlesim/msg/Pose
```

속도 토픽의 타입도 확인할 수 있다.

``` bash
ros2 topic type /turtle1/cmd_vel
```

예상 결과:

``` text
geometry_msgs/msg/Twist
```

------------------------------------------------------------------------

## 6. e0509 Dart 프로그램 실행 방법 확인하기 (IP 주소 및 비밀번호)

이 항목의 **e0509이 어떤 장비·프로그램·수업 자료를 가리키는지는 현재
정보만으로 확정할 수 없다.** 따라서 아래는 Linux에서 IP 주소를 확인하는
일반적인 방법이다. Dart 프로그램의 실제 실행 명령은 제공된 프로젝트의
README나 수업 안내에 맞춰야 한다.

### 6-1. IP 주소 확인

``` bash
ip addr
```

또는 현재 네트워크에서 사용할 수 있는 주소를 간단히 확인한다.

``` bash
hostname -I
```

-   `lo`의 `127.0.0.1`은 자기 컴퓨터 내부 통신용 주소이므로 보통 다른
    장비에서 접속할 때 쓰지 않는다.
-   Wi-Fi나 유선 네트워크 인터페이스에 표시되는 주소를 확인한다.
-   IP 주소는 네트워크가 바뀌거나 공유기가 주소를 다시 할당하면 달라질
    수 있다.

### 6-2. Dart 설치 여부 확인

``` bash
dart --version
```

Dart가 설치되어 있지 않거나 명령어를 찾지 못한다면 설치 여부와 PATH
설정을 확인한다.

### 6-3. Dart 프로젝트 실행

프로젝트 폴더에 `pubspec.yaml`이 있다면 해당 폴더로 이동해 보통 다음
순서로 실행한다.

``` bash
cd /프로젝트/폴더/경로
dart pub get
dart run
```

실행 파일을 지정하는 프로젝트라면 수업 안내에 따라 파일명을 지정한다.

``` bash
dart run bin/main.dart
```

위 명령은 **일반적인 예시**이며, e0509 프로젝트가 Flutter 앱이거나
별도의 실행 스크립트를 사용하는 경우에는 실행 방법이 다를 수 있다.

### 6-4. 비밀번호 관련 주의

-   비밀번호는 터미널에 입력해도 화면에 글자나 별표가 표시되지 않는
    경우가 있다. 입력 후 `Enter`를 누르면 된다.
-   본인 계정 비밀번호만 사용한다.
-   비밀번호를 GitHub README, 코드, 공개 이슈, 스크린샷에 올리지 않는다.
-   원격 접속용 IP와 계정 정보가 필요한 실습이라면 수업에서 제공한 접속
    안내를 따른다. 비밀번호를 공개 저장소에 저장하지 않는다.

**완료하려면 확인할 것:** e0509의 수업 안내 또는 프로젝트 README에서
정확한 실행 명령, 접속 대상 IP, 인증 방식을 확인한다.

------------------------------------------------------------------------

## 7. `ros2 service list`와 `ros2 service call` 실행하기

ROS 2 Service는 일반적으로 **요청(Request)을 보내고 응답(Response)을
받는 통신 방식**이다.

### 7-1. 실행 중인 서비스 목록 확인

`turtlesim_node`가 실행 중인 터미널을 둔 채 다른 터미널에서 실행한다.

``` bash
source /opt/ros/jazzy/setup.bash
ros2 service list
```

서비스 목록에는 실행 환경에 따라 다음과 같은 이름이 나타날 수 있다.

``` text
/clear
/reset
/spawn
/teleport_absolute
/turtle1/set_pen
/turtle1/teleport_absolute
```

### 7-2. 서비스 타입 확인

``` bash
ros2 service type /turtle1/set_pen
```

예상 결과:

``` text
turtlesim/srv/SetPen
```

서비스의 요청 형식은 다음처럼 확인할 수 있다.

``` bash
ros2 interface show turtlesim/srv/SetPen
```

예상 형식:

``` text
uint8 r
uint8 g
uint8 b
uint8 width
uint8 off
---
```

`---` 위는 Request 필드, 아래는 Response 필드다. `SetPen`의 Response에는
별도 필드가 없으며, 호출 성공 여부는 서비스 응답 처리 결과를 통해
확인한다.

### 7-3. 거북이 펜 색상 변경

다음 명령은 거북이의 펜 색을 빨간색으로 바꾸는 예시다.

``` bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 3, off: 0}"
```

필드 뜻:

  필드      의미
  --------- ----------------------------------
  `r`       빨강 값 (0\~255)
  `g`       초록 값 (0\~255)
  `b`       파랑 값 (0\~255)
  `width`   펜 굵기
  `off`     `1`이면 펜 끄기, `0`이면 펜 켜기

### 7-4. 두 번째 거북이 생성 서비스 예시

``` bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```

이 서비스는 지정한 위치와 방향에 거북이를 생성하고, 응답으로 생성된
거북이의 이름을 돌려준다. 이미 `turtle2`가 있다면 다른 이름을 사용한다.

------------------------------------------------------------------------

## 8. 도전: Turtlesim 펜 설정 `/set_pen`의 Request와 Response

### 서비스 이름과 타입

-   서비스 이름: `/turtle1/set_pen`
-   서비스 타입: `turtlesim/srv/SetPen`

확인 명령어:

``` bash
ros2 service type /turtle1/set_pen
ros2 interface show turtlesim/srv/SetPen
```

### Request 형태

``` text
uint8 r
uint8 g
uint8 b
uint8 width
uint8 off
```

예를 들어 다음 호출은 초록색 펜, 굵기 3, 펜 켜기를 요청한다.

``` bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 0, g: 255, b: 0, width: 3, off: 0}"
```

요청 값:

``` yaml
r: 0
g: 255
b: 0
width: 3
off: 0
```

### Response 형태

`SetPen` 서비스 인터페이스의 `---` 뒤에는 응답 필드가 정의되어 있지
않다. 즉, **별도의 데이터 필드가 없는 빈 Response**다.

이것은 Request가 없다는 뜻이 아니다. 색상과 굵기 설정은 Request로
보내고, Response에는 반환할 별도 값이 없는 구조다.

------------------------------------------------------------------------

## 9. 실습 완료 체크리스트

-   [ ] Linux 명령어 5개 이상 직접 실행했다.
-   [ ] `pwd`, `ls`, `cd`로 현재 경로와 디렉터리 이동을 확인했다.
-   [ ] ROS 2 Jazzy 환경을 `source`했다.
-   [ ] `colcon build`를 실행했다.
-   [ ] `source install/setup.bash` 후 패키지 실행을 확인했다.
-   [ ] Node / Topic / Publisher / Subscriber를 한 문장씩 설명할 수
    있다.
-   [ ] Lesson 3 subscriber 코드에서 Topic 이름을 찾았다.
-   [ ] Lesson 3 subscriber 코드에서 Message type을 찾았다.
-   [ ] Lesson 3 subscriber 코드에서 Callback 함수를 찾았다.
-   [ ] `ros2 topic list`를 실행했다.
-   [ ] `ros2 topic echo /turtle1/pose`를 실행했다.
-   [ ] `ros2 service list`를 실행했다.
-   [ ] `ros2 service call`로 펜 색상을 변경했다.
-   [ ] `SetPen`의 Request와 Response 구조를 확인했다.
-   [ ] e0509 Dart 프로젝트의 정확한 실행 안내를 확인했다.
-   [ ] 비밀번호 등 비밀 정보를 GitHub에 올리지 않았는지 확인했다.

------------------------------------------------------------------------

## 10. GitHub에 올리기

README 파일을 학습 저장소의 적절한 폴더에 저장한 다음, 저장소 루트에서
아래 명령어를 실행한다.

``` bash
git status
git add README.md
git commit -m "Add Linux and ROS 2 basic practice notes"
git push
```

README가 하위 폴더에 있다면 `git add README.md` 대신 실제 경로를
지정한다. 예를 들어:

``` bash
git add 01_ros2_basics/README.md
```

현재 브랜치와 GitHub 원격 저장소 설정에 따라 `git push` 명령이 달라질 수
있다. `git status`로 변경 사항을 먼저 확인한다.
