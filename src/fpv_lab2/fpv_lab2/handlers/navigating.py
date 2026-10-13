import math
import time
from typing import TYPE_CHECKING

from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class NavigatingHandler(FlightStateHandler):
    def __init__(self) -> None:
        self.in_zone_since = None
        self.last_log = 0.0

    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during navigation")
            return
        if node.odometry is None or node.target_x is None:
            return

        pos = node.odometry.pose.pose.position
        ex = node.target_x - pos.x
        ey = node.target_y - pos.y
        dist = math.hypot(ex, ey)
        now = time.monotonic()

        if now - self.last_log >= 1.0:
            self.last_log = now
            node.get_logger().info(
                f"Position ({pos.x:.2f}, {pos.y:.2f}), "
                f"distance to target {dist:.2f} m")

        if dist <= node.POSITION_TOLERANCE:
            node.send_velocity(0.0, 0.0)
            if self.in_zone_since is None:
                self.in_zone_since = now
                node.get_logger().info("Target zone reached, stopping")
            elif now - self.in_zone_since >= node.SETTLE_TIME:
                node.get_logger().info(
                    f"Start:  ({node.start_x:.3f}, {node.start_y:.3f})")
                node.get_logger().info(
                    f"Target: ({node.target_x:.3f}, {node.target_y:.3f})")
                node.get_logger().info(
                    f"Actual: ({pos.x:.3f}, {pos.y:.3f})")
                node.get_logger().info(
                    f"Position error: {dist:.3f} m. Starting landing")
                node.state = FlightState.LANDING
            return

        self.in_zone_since = None
        speed = min(node.MAX_SPEED, node.KP * dist)
        node.send_velocity(speed * ex / dist, speed * ey / dist)
