#!/bin/bash

set -e

export DISPLAY=:1

echo "Starting virtual display..."

Xvfb :1 \
  -screen 0 1600x900x24 \
  -ac +extension GLX +render \
  -noreset &

sleep 2

echo "Starting VNC server..."

x11vnc \
  -display :1 \
  -forever \
  -shared \
  -nopw \
  -rfbport 5900 \
  -listen 0.0.0.0 &

sleep 2

echo "Starting noVNC..."

websockify \
  --web=/usr/share/novnc \
  6080 \
  127.0.0.1:5900 &

echo "Starting XFCE desktop..."

exec dbus-run-session -- startxfce4
