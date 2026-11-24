# ROS 2 + Gazebo Docker Environment

A ready-to-use robotics setup for macOS on Apple Silicon. You edit code on your Mac, ROS 2 and Gazebo run inside Docker, and you see the Linux desktop in your browser.

> **Stack:** Ubuntu 24.04 (ARM64) · ROS 2 Jazzy · Gazebo Harmonic · RViz2 · XFCE desktop via noVNC

```text
ros2-docker/
├── Dockerfile          # What is installed in the image
├── compose.yaml        # How the container runs (port, shared folder)
├── start-desktop.sh    # Starts the virtual desktop and noVNC
└── workspace/          # Shared with the container as /workspace
    └── src/            # Your ROS packages and scripts go here
```

## Contents

1. [How it works](#how-it-works)
2. [Before you start](#before-you-start)
3. [First-time setup](#first-time-setup)
4. [Everyday commands](#everyday-commands)
5. [Use cases](#use-cases)
   - [Just write code](#1-just-write-code)
   - [Check that ROS works](#2-check-that-ros-works)
   - [Run a Python script](#3-run-a-python-script)
   - [Create and build your own package](#4-create-and-build-your-own-package)
   - [Open RViz2 or Gazebo](#5-open-rviz2-or-gazebo)
   - [Connect Gazebo to ROS 2](#6-connect-gazebo-to-ros-2)
   - [Inspect what is running](#7-inspect-what-is-running)
6. [Troubleshooting](#troubleshooting)
7. [Good to know](#good-to-know)

## How it works

| I want to...           | Where to do it                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Edit code              | VS Code on your Mac, in `workspace/src/`                                                |
| Start or stop Docker   | Mac Terminal, in `~/robotics/ros2-docker`                                               |
| Build and run ROS code | Container shell: `docker compose exec ros bash`                                         |
| See Gazebo or RViz2    | Browser: [localhost:6080](http://localhost:6080/vnc.html?autoconnect=true&resize=scale) |

> **Tip:** ROS is loaded automatically in every container shell. You only need `source /workspace/install/setup.bash` after building your own packages.

## Before you start

- A Mac with Apple Silicon (M1 or newer).
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Suggested Docker Desktop resources (**Settings → Resources**): 6 CPUs, 10–12 GB RAM, 60 GB disk.

## First-time setup

On your **Mac**:

```bash
cd ~/robotics/ros2-docker
docker compose up -d --build     # first build takes several minutes
docker compose ps                # STATUS should say "Up"
```

Check the installation from inside the container:

```bash
docker compose exec ros bash     # opens a shell inside the container
echo $ROS_DISTRO                 # → jazzy
gz sim --versions                # → 8.x
exit                             # leaves the shell; the container keeps running
```

## Everyday commands

Run these on your **Mac**, from `~/robotics/ros2-docker`.

| Command                        | What it does                                                  |
| ------------------------------ | ------------------------------------------------------------- |
| `docker compose up -d`         | Start the container                                           |
| `docker compose exec ros bash` | Open a shell inside it (run again for more terminals)         |
| `docker compose down`          | Stop and remove the container (`workspace/` is safe)          |
| `docker compose restart ros`   | Restart the container                                         |
| `docker compose ps`            | Check whether it is running                                   |
| `docker compose logs -f ros`   | Follow the logs (`Ctrl+C` stops following, not the container) |
| `docker compose up -d --build` | Rebuild after changing `Dockerfile` or `start-desktop.sh`     |

> The container starts automatically with Docker Desktop until you run `docker compose down`.

## Use cases

Start the container first (`docker compose up -d`). Unless a step says **Mac**, run the commands in a container shell (`docker compose exec ros bash`).

### 1. Just write code

On your **Mac**, open `~/robotics/ros2-docker` in VS Code and edit files in `workspace/src/`. Changes appear instantly in the container under `/workspace/src/`. No browser needed.

Helpful VS Code extensions: **ROS**, **Python**, and **C/C++** (all by Microsoft).

### 2. Check that ROS works

Open two container shells and run:

- **Terminal 1:** `ros2 run demo_nodes_cpp talker`
- **Terminal 2:** `ros2 run demo_nodes_py listener`

Terminal 2 prints `I heard: [Hello World: N]`. Press `Ctrl+C` to stop.

### 3. Run a Python script

```bash
python3 /workspace/src/hello_robot/robot.py
```

It prints `Published: Hello #N` and `Received: Hello #N` every second. Press `Ctrl+C` to stop.

### 4. Create and build your own package

```bash
cd /workspace/src
ros2 pkg create --build-type ament_python --license Apache-2.0 --node-name my_node my_robot
cd /workspace
colcon build --symlink-install
source install/setup.bash
ros2 run my_robot my_node        # → Hi from my_robot.
```

- **C++ package:** use `--build-type ament_cmake` instead.
- **Build one package:** `colcon build --symlink-install --packages-select my_robot`
- **New shell?** Run `source /workspace/install/setup.bash` again.
- **After edits:** restart the node for Python changes; rebuild for C++ changes.

### 5. Open RViz2 or Gazebo

1. On your **Mac**, open [localhost:6080](http://localhost:6080/vnc.html?autoconnect=true&resize=scale) in a browser.
2. In a container shell (or a terminal inside that desktop), run one of:

```bash
rviz2                                # ROS data visualizer
gz sim shapes.sdf                    # Gazebo with a built-in sample world
gz sim /workspace/path/to/world.sdf  # Gazebo with your own world
```

The window appears in the browser tab. RViz2 starts empty until you add displays and something publishes ROS topics.

### 6. Connect Gazebo to ROS 2

Gazebo and ROS 2 do not share topics automatically; a bridge connects them. This example sends Gazebo's simulation clock to ROS, using three container shells:

1. **Terminal 1** (start Gazebo and run the simulation right away): `gz sim -r shapes.sdf`
2. **Terminal 2** (bridge `/clock` from Gazebo to ROS): `ros2 run ros_gz_bridge parameter_bridge "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"`
3. **Terminal 3** (confirm ROS receives it): `ros2 topic echo /clock`

The symbol between the two message types sets the direction: `[` is Gazebo to ROS, `]` is ROS to Gazebo, and `@` is both ways. A full simulation usually runs Gazebo, the bridge, your nodes, and RViz2, each in its own terminal.

### 7. Inspect what is running

| Command                  | Shows                                          |
| ------------------------ | ---------------------------------------------- |
| `ros2 node list`         | Running nodes                                  |
| `ros2 topic list`        | Available topics                               |
| `ros2 topic echo /topic` | Live messages on a topic                       |
| `ros2 topic hz /topic`   | How often a topic publishes                    |
| `ros2 node info /node`   | A node's publishers, subscribers, and services |
| `gz topic -l`            | Gazebo topics                                  |

## Troubleshooting

| Problem                                      | Fix                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------ |
| `localhost:6080` does not load               | Check `docker compose ps` and `docker compose logs --tail=100 ros`             |
| Container keeps stopping or restarting       | Read `docker compose logs --tail=150 ros`; the desktop startup failed          |
| `service "ros" is not running`               | Run `docker compose up -d` first                                               |
| `rviz2` cannot open a display                | Run it from a container shell; `echo $DISPLAY` should print `:1`               |
| Gazebo is black, slow, or crashes            | Software rendering limit; try a simpler world and check `glxinfo -B`           |
| `Package '...' not found`                    | `cd /workspace && colcon build --symlink-install && source install/setup.bash` |
| Code changes have no effect                  | Rebuild the package, source the workspace again, and restart the node          |
| Nodes in two terminals cannot see each other | Run both in this container with the same `ROS_DOMAIN_ID`                       |
| A package installed with `apt` is gone       | Add it to the `Dockerfile`, then run `docker compose up -d --build`            |
| Docker keeps using an old build              | `docker compose build --no-cache && docker compose up -d`                      |

## Good to know

- **What is saved:** everything in `workspace/` lives on your Mac and survives restarts, `docker compose down`, and rebuilds. Other changes made inside the container are lost when it is recreated.
- **Clean build files:** run `rm -rf workspace/build workspace/install workspace/log` on your Mac. Your code in `workspace/src/` is not touched.
- **ARM64 only:** any extra package you add must support `linux/arm64`.
- **No GPU:** Docker on macOS uses software rendering, so complex Gazebo scenes are slow.
- **Security:** noVNC has no password and only listens on `127.0.0.1` (your Mac). Do not change the port binding to `0.0.0.0`.
- **Gazebo vs RViz2:** Gazebo *simulates* the robot; RViz2 *visualizes* ROS data. They are often used together.
- **Purpose:** this is for learning and development, not for real-time or production robot control.

> **Remember:** edit on the Mac, build and run in Docker, and open the browser only when you need a GUI.
