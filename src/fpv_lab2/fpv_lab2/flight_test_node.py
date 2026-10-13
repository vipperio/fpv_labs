from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger
from geometry_msgs.msg import TwistStamped
from ardupilot_msgs.msg import Status
from ardupilot_msgs.srv import ArmMotors, ModeSwitch, Takeoff

from .flight_state import FlightState
from .handlers import HANDLERS


class FlightTestNode(Node):
    GUIDED_MODE = 4
    LAND_MODE = 9
    TAKEOFF_ALTITUDE = 2.0
    HOVER_DURATION = 30.0

    TARGET_DX = 4.0               # variant 13
    TARGET_DY = 0.2
    MAX_SPEED = 1.0
    KP = 0.8
    POSITION_TOLERANCE = 0.15
    SETTLE_TIME = 2.0
    CMD_VEL_TOPIC = "/ap/v1/cmd_vel"

    def __init__(self):
        super().__init__("flight_test")
        self.declare_parameter("navigate", False)
        self.navigate = self.get_parameter("navigate").value
        if self.navigate:
            self.HOVER_DURATION = 5.0

        self.state = FlightState.WAITING_FOR_SYSTEM
        self.request_in_progress = False
        self.status = None
        self.odometry = None
        self.hover_started_at = None
        self.start_x = self.start_y = self.start_z = None
        self.target_x = self.target_y = None
        self._handlers = HANDLERS

        self.status_subscription = self.create_subscription(
            Status, "/ap/v1/status", self.status_callback, 10)
        self.odometry_subscription = self.create_subscription(
            Odometry, "/odometry", self.odometry_callback, 10)

        self.cmd_vel_publisher = self.create_publisher(
            TwistStamped, self.CMD_VEL_TOPIC, 10)

        self.prearm_client = self.create_client(Trigger, "/ap/v1/prearm_check")
        self.mode_client = self.create_client(ModeSwitch, "/ap/v1/mode_switch")
        self.arm_client = self.create_client(ArmMotors, "/ap/v1/arm_motors")
        self.takeoff_client = self.create_client(
            Takeoff, "/ap/v1/experimental/takeoff")

        self.timer = self.create_timer(0.2, self.control_loop)
        self.get_logger().info("Flight test node started")
        self.get_logger().info("Waiting for ArduPilot and ROS services...")

    def status_callback(self, message):
        self.status = message

    def odometry_callback(self, message):
        self.odometry = message
        if self.start_x is None:
            p = message.pose.pose.position
            self.start_x, self.start_y, self.start_z = p.x, p.y, p.z
            self.target_x = self.start_x - self.TARGET_DX
            self.target_y = self.start_y - self.TARGET_DY
            self.get_logger().info(
                f"Start: ({self.start_x:.2f}, {self.start_y:.2f}); "
                f"Target: ({self.target_x:.2f}, {self.target_y:.2f})")

    def send_velocity(self, vx, vy):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.twist.linear.x = float(vx)
        msg.twist.linear.y = float(vy)
        msg.twist.linear.z = 0.0
        self.cmd_vel_publisher.publish(msg)

    def services_ready(self):
        return (
            self.prearm_client.service_is_ready()
            and self.mode_client.service_is_ready()
            and self.arm_client.service_is_ready()
            and self.takeoff_client.service_is_ready()
        )

    def control_loop(self):
        handler = self._handlers.get(self.state)
        if handler is not None:
            handler.handle(self)

    def call_mode_switch(self, mode, callback):
        self.request_in_progress = True
        request = ModeSwitch.Request()
        request.mode = mode
        future = self.mode_client.call_async(request)
        future.add_done_callback(callback)
        self.get_logger().info(f"Requesting flight mode {mode}")

    def fail(self, message):
        self.get_logger().error(message)
        self.state = FlightState.ERROR
