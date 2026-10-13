#!/usr/bin/env bash
ARDU_WS="${ARDU_WS:-$HOME/ardu_ws}"
LAB_WS="${LAB_WS:-$HOME/fpv_labs}"
export GZ_VERSION=harmonic
source /opt/ros/humble/setup.bash
source "$ARDU_WS/install/setup.bash"
source "$LAB_WS/install/setup.bash"
ros2 run fpv_lab2 flight_test 2>&1 | tee "$LAB_WS/flight_$(date +%H%M%S).log"
