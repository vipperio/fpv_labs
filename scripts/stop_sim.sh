#!/usr/bin/env bash
tmux kill-session -t sim 2>/dev/null
pkill -f "gz sim" 2>/dev/null
pkill -f arducopter 2>/dev/null
pkill -f mavproxy 2>/dev/null
pkill -f micro_ros_agent 2>/dev/null
pkill -f robot_state_publisher 2>/dev/null
echo "Процеси симуляції зупинено"
