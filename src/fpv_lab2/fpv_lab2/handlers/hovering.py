import time
from typing import TYPE_CHECKING

from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class HoveringHandler(FlightStateHandler):
    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during flight")
            return

        if node.odometry is not None and node.start_z is not None:
            altitude = node.odometry.pose.pose.position.z - node.start_z
            if altitude < 0.9 * node.TAKEOFF_ALTITUDE:
                node.hover_started_at = time.monotonic()
                return

        elapsed = time.monotonic() - node.hover_started_at
        if elapsed >= node.HOVER_DURATION:
            if node.navigate:
                node.get_logger().info("Hover completed, starting navigation")
                node.state = FlightState.NAVIGATING
            else:
                node.get_logger().info("Hover completed, starting landing")
                node.state = FlightState.LANDING
