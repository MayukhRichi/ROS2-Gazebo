import rclpy
from rclpy.node import Node
from std_msgs.msg import String


# NODE 1: Publisher
class HelloRobot(Node):

    def __init__(self):
        super().__init__('hello_robot')

        self.publisher = self.create_publisher(
            String,
            '/robot_status',
            10
        )

        self.counter = 0

        self.timer = self.create_timer(
            1.0,
            self.publish_status
        )

    def publish_status(self):

        msg = String()
        msg.data = f'Hello #{self.counter}'

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Published: {msg.data}'
        )

        self.counter += 1


# NODE 2: Subscriber
class RobotMonitor(Node):

    def __init__(self):
        super().__init__('robot_monitor')

        self.subscription = self.create_subscription(
            String,
            '/robot_status',
            self.status_callback,
            10
        )

    def status_callback(self, msg):

        self.get_logger().info(
            f'Received: {msg.data}'
        )


# MAIN
def main(args=None):

    rclpy.init(args=args)

    publisher = HelloRobot()
    subscriber = RobotMonitor()

    # Run both nodes using a single executor
    executor = rclpy.executors.SingleThreadedExecutor()

    executor.add_node(publisher)
    executor.add_node(subscriber)

    try:
        executor.spin()

    except KeyboardInterrupt:
        pass

    finally:
        executor.shutdown()
        publisher.destroy_node()
        subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
