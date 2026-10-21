#!/usr/bin/env bash
# Лаба 7: Gazebo + ArduPilot SITL (+MAVProxy на UDP 14550) і QGroundControl
"$HOME/fpv_labs/scripts/start_sim.sh"
echo "Чекаю запуск симуляції (90 с)..."
sleep 90
nohup "$HOME/qgc/QGroundControl.AppImage" > "$HOME/fpv_labs/lab7/qgc_stdout.log" 2>&1 &
echo "QGroundControl запущено. Gazebo-лог: tmux attach -t sim"
