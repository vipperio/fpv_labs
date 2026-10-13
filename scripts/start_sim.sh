#!/usr/bin/env bash
ARDU_WS="${ARDU_WS:-$HOME/ardu_ws}"
"$(dirname "$0")/stop_sim.sh"
sleep 2
tmux new-session -d -s sim "bash -lc '
export GZ_VERSION=harmonic
source /opt/ros/humble/setup.bash
source $ARDU_WS/install/setup.bash
ros2 launch ardupilot_gz_bringup iris_maze.launch.py rviz:=false 2>&1 | tee ~/launch.log; exec bash'"
echo "Середовище запускається (2-4 хв у ВМ). Логи: tmux attach -t sim (вихід: Ctrl+B, потім D)"
