# ROS 2 Topic 01 - 거북이 위치 구독하기

## 1. 실습 목표

ROS 2의 Subscriber 개념을 이해하고,
`/turtle1/pose` 토픽을 구독하여 거북이의 위치와 방향을 출력한다.

## 2. 개발 환경

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python
- turtlesim

## 3. 핵심 개념

| 개념 | 설명 |
|---|---|
| Node | ROS 2에서 기능을 수행하는 실행 단위 |
| Topic | 노드 간 메시지를 전달하는 통신 방식 |
| Subscriber | 토픽의 메시지를 구독하는 노드 |
| Callback | 메시지가 도착했을 때 실행되는 함수 |
| Pose | 거북이의 위치와 방향을 담는 메시지 |

## 4. 통신 구조

```text
turtlesim_node
      |
      | Publish
      v
/turtle1/pose
      |
      | Subscribe
      v
PoseSubscriber
      |
      v
x, y, theta 출력