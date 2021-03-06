import sys, signal, logging
from time import time, sleep
import numpy as np
from autolab_core import RigidTransform
import quaternion
from itertools import product

import roslib
roslib.load_manifest('franka_interface_msgs')
import rospy
import actionlib
from sensor_msgs.msg import JointState
from franka_interface_msgs.msg import ExecuteSkillAction, FrankaInterfaceStatus
from franka_interface_msgs.srv import GetCurrentFrankaInterfaceStatusCmd

from .skill_list import *
from .exceptions import *
from .franka_arm_state_client import FrankaArmStateClient
from .franka_constants import FrankaConstants as FC
from .franka_interface_common_definitions import *
from .ros_utils import BoxesPublisher


class FrankaArm:

    def __init__(
            self,
            rosnode_name='franka_arm_client', ros_log_level=rospy.INFO,
            robot_num=1,
            offline=False):

        self._execute_skill_action_server_name = \
                '/execute_skill_action_server_node_{}/execute_skill'.format(robot_num)
        self._robot_state_server_name = \
                '/get_current_robot_state_server_node_{}/get_current_robot_state_server'.format(robot_num)
        self._franka_interface_status_server_name = \
                '/get_current_franka_interface_status_server_node_{}/get_current_franka_interface_status_server'.format(robot_num)

        self._connected = False
        self._in_skill = False
        self._offline = offline

        # init ROS
        rospy.init_node(rosnode_name,
                        disable_signals=True,
                        log_level=ros_log_level)
        self._collision_boxes_pub = BoxesPublisher('franka_collision_boxes_{}'.format(robot_num))
        self._joint_state_pub = rospy.Publisher('franka_virtual_joints_{}'.format(robot_num), JointState, queue_size=10)
        
        self._state_client = FrankaArmStateClient(
                new_ros_node=False,
                robot_state_server_name=self._robot_state_server_name,
                offline=self._offline)

        if not self._offline:
            # set signal handler to handle ctrl+c and kill sigs
            signal.signal(signal.SIGINT, self._sigint_handler_gen())
            
            rospy.wait_for_service(self._franka_interface_status_server_name)
            self._get_current_franka_interface_status = rospy.ServiceProxy(
                    self._franka_interface_status_server_name, GetCurrentFrankaInterfaceStatusCmd)

            self._client = actionlib.SimpleActionClient(
                    self._execute_skill_action_server_name, ExecuteSkillAction)
            self._client.wait_for_server()
            self.wait_for_franka_interface()

            # done init ROS
            self._connected = True

        # set default identity tool delta pose
        self._tool_delta_pose = RigidTransform(from_frame='franka_tool', to_frame='franka_tool_base')

        # Precompute things and preallocate np memory for collision checking
        self._collision_boxes_data = np.zeros((len(FC.COLLISION_BOX_SHAPES), 10))
        self._collision_boxes_data[:, -3:] = FC.COLLISION_BOX_SHAPES

        self._collision_box_hdiags = []
        self._collision_box_vertices_offset = []
        self._vertex_offset_signs = np.array(list(product([1, -1],[1,-1], [1,-1])))
        for sizes in FC.COLLISION_BOX_SHAPES:
            hsizes = sizes/2
            self._collision_box_vertices_offset.append(self._vertex_offset_signs * hsizes)
            self._collision_box_hdiags.append(np.linalg.norm(sizes/2))
        self._collision_box_vertices_offset = np.array(self._collision_box_vertices_offset)
        self._collision_box_hdiags = np.array(self._collision_box_hdiags)

        self._collision_proj_axes = np.zeros((3, 15))
        self._box_vertices_offset = np.ones([8, 3])
        self._box_transform = np.eye(4)

    def wait_for_franka_interface(self, timeout=None):
        '''Blocks execution until franka_interface gives ready signal.
        '''
        timeout = FC.DEFAULT_FRANKA_INTERFACE_TIMEOUT if timeout is None else timeout
        t_start = time()
        while time() - t_start < timeout:
            franka_interface_status = self._get_current_franka_interface_status().franka_interface_status
            if franka_interface_status.is_ready:
                return
            sleep(1e-2)
        raise FrankaArmCommException('FrankaInterface status not ready for {}s'.format(
            FC.DEFAULT_FRANKA_INTERFACE_TIMEOUT))

    def wait_for_skill(self):
        while not self.is_skill_done():
            continue

    def is_skill_done(self, ignore_errors=True):  
        if not self._in_skill:  
            return True 

        franka_interface_status = self._get_current_franka_interface_status().franka_interface_status  

        e = None  
        if rospy.is_shutdown(): 
            e = RuntimeError('rospy is down!')  
        elif franka_interface_status.error_description:  
            e = FrankaArmException(franka_interface_status.error_description)  
        elif not franka_interface_status.is_ready: 
            e = FrankaArmFrankaInterfaceNotReadyException() 

        if e is not None: 
            if ignore_errors: 
                self.wait_for_franka_interface() 
            else: 
                raise e 

        done = self._client.wait_for_result(rospy.Duration.from_sec(  
            FC.ACTION_WAIT_LOOP_TIME))

        if done:  
            self._in_skill = False  

        return done

    def stop_skill(self): 
        if self._connected and self._in_skill:
            self._client.cancel_goal()
        self.wait_for_skill()

    def _sigint_handler_gen(self):
        def sigint_handler(sig, frame):
            if self._connected and self._in_skill:
                self._client.cancel_goal()
            sys.exit(0)

        return sigint_handler

    def _send_goal(self, goal, cb, block=True, ignore_errors=True):
        '''
        Raises:
            FrankaArmCommException if a timeout is reached
            FrankaArmException if franka_interface gives an error
            FrankaArmFrankaInterfaceNotReadyException if franka_interface is not ready
        '''
        if self._offline:
            logging.warn('In offline mode, FrankaArm will not execute real robot commands.')
            return

        if not self.is_skill_done():  
            raise ValueError('Cannot send another command when the previous skill is active!')

        self._in_skill = True
        self._client.send_goal(goal, feedback_cb=cb)

        if not block:  
            return None

        self.wait_for_skill()
        return self._client.get_result()

    '''
    Controls
    '''

    def goto_pose(self,
                  tool_pose,
                  duration=3,
                  use_impedance=True,
                  dynamic=False,
                  buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                  force_thresholds=None,
                  torque_thresholds=None,
                  cartesian_impedances=None,
                  joint_impedances=None,
                  block=True,
                  ignore_errors=True,
                  ignore_virtual_walls=False,
                  skill_desc='GoToPose'):
        '''Commands Arm to the given pose via min jerk interpolation

        Args:
            tool_pose (RigidTransform) : End-effector pose in tool frame
            duration (float) : How much time this robot motion should take
            use_impedance (boolean) : Function uses our impedance controller 
                by default. If False, uses the Franka cartesian controller.
            dynamic (boolean) : Flag that states whether the skill is dynamic.  
                If True, it will use our joint impedance controller and sensor values.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            ignore_virtual_walls (boolean): Function checks for collisions with 
                virtual walls by default. If False, the robot no longer checks,
                which may be dangerous.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''
        if dynamic:
            skill = Skill(SkillType.ImpedanceControlSkill, 
                          TrajectoryGeneratorType.PassThroughPoseTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                          skill_desc=skill_desc)
            use_impedance=True
            block = False
        else:
            if use_impedance:
                skill = Skill(SkillType.ImpedanceControlSkill, 
                              TrajectoryGeneratorType.MinJerkPoseTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalPoseTerminationHandler, 
                              skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.CartesianPoseSkill, 
                              TrajectoryGeneratorType.MinJerkPoseTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalPoseTerminationHandler, 
                              skill_desc=skill_desc)
        
        if tool_pose.from_frame != 'franka_tool' or tool_pose.to_frame != 'world':
            raise ValueError('pose has invalid frame names! Make sure pose has \
                              from_frame=franka_tool and to_frame=world')

        tool_base_pose = tool_pose * self._tool_delta_pose.inverse()

        if not ignore_virtual_walls and np.any([
            tool_base_pose.translation <= FC.WORKSPACE_WALLS[:, :3].min(axis=0),
            tool_base_pose.translation >= FC.WORKSPACE_WALLS[:, :3].max(axis=0)]):
            raise ValueError('Target pose is outside of workspace virtual walls!')

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)

        skill.set_cartesian_impedances(use_impedance, cartesian_impedances, joint_impedances)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            if dynamic:
                skill.add_time_termination_params(buffer_time)
            else:
                skill.add_pose_threshold_params(buffer_time, FC.DEFAULT_POSE_THRESHOLDS)

        skill.add_goal_pose(duration, tool_base_pose)
        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

        if dynamic:
            sleep(FC.DYNAMIC_SKILL_WAIT_TIME)

    def goto_pose_delta(self,
                        delta_tool_pose,
                        duration=3,
                        use_impedance=True,
                        buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                        force_thresholds=None,
                        torque_thresholds=None,
                        cartesian_impedances=None,
                        joint_impedances=None,
                        block=True,
                        ignore_errors=True,
                        ignore_virtual_walls=False,
                        skill_desc='GoToPoseDelta'):
        '''Commands Arm to the given delta pose via min jerk interpolation

        Args:
            delta_tool_pose (RigidTransform) : Delta pose in tool frame
            duration (float) : How much time this robot motion should take
            use_impedance (boolean) : Function uses our impedance controller 
                by default. If False, uses the Franka cartesian controller.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            ignore_virtual_walls (boolean): Function checks for collisions with 
                virtual walls by default. If False, the robot no longer checks,
                which may be dangerous.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''
        if use_impedance:
            skill = Skill(SkillType.ImpedanceControlSkill, 
                          TrajectoryGeneratorType.RelativeMinJerkPoseTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.FinalPoseTerminationHandler, 
                          skill_desc=skill_desc)
        else:
            skill = Skill(SkillType.CartesianPoseSkill, 
                          TrajectoryGeneratorType.RelativeMinJerkPoseTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.FinalPoseTerminationHandler, 
                          skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)

        skill.set_cartesian_impedances(use_impedance, cartesian_impedances, joint_impedances)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_pose_threshold_params(buffer_time, FC.DEFAULT_POSE_THRESHOLDS)

        if delta_tool_pose.from_frame == 'world' \
                and delta_tool_pose.to_frame == 'world':

            skill.add_goal_pose(duration, delta_tool_pose)

        elif delta_tool_pose.from_frame == 'franka_tool' \
                and delta_tool_pose.to_frame == 'franka_tool':
            starting_pose = self.get_pose()

            starting_tool_base_pose = starting_pose * self._tool_delta_pose.inverse()

            final_goal_pose = starting_pose * delta_tool_pose

            final_tool_base_pose = final_goal_pose * self._tool_delta_pose.inverse()

            delta_tool_base_pose = starting_tool_base_pose.inverse() * final_tool_base_pose

            starting_rotation = RigidTransform(
                rotation=starting_pose.rotation,
                from_frame='franka_tool', to_frame='franka_tool'
            )
            predicted_translation = RigidTransform(
                translation=delta_tool_base_pose.translation,
                from_frame='franka_tool', to_frame='franka_tool'
            )
            actual_translation = starting_rotation * predicted_translation
            delta_tool_base_pose.translation = actual_translation.translation

            if not ignore_virtual_walls and not self._offline:
                if np.any([
                    final_tool_base_pose.translation <= FC.WORKSPACE_WALLS[:, :3].min(axis=0),
                    final_tool_base_pose.translation >= FC.WORKSPACE_WALLS[:, :3].max(axis=0)]):
                    raise ValueError('Target pose is outside of workspace virtual walls!')

            skill.add_goal_pose(duration, delta_tool_base_pose)

        else:
            raise ValueError('delta_pose has invalid frame names! ' \
                             'Make sure delta_pose has from_frame=franka_tool ' \
                             'and to_frame=franka_tool or from_frame=world and \
                             to_frame=world')

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)
            

    def goto_joints(self,
                    joints,
                    duration=5,
                    use_impedance=False,
                    dynamic=False,
                    buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                    force_thresholds=None,
                    torque_thresholds=None,
                    cartesian_impedances=None,
                    joint_impedances=None,
                    k_gains=None,
                    d_gains=None,
                    block=True,
                    ignore_errors=True,
                    ignore_virtual_walls=False,
                    skill_desc='GoToJoints'):
        '''Commands Arm to the given joint configuration

        Args:
            joints (list): A list of 7 numbers that correspond to joint angles
                           in radians
            duration (float): How much time this robot motion should take
            use_impedance (boolean) : Function uses the Franka joint impedance  
                controller by default. If True, uses our joint impedance controller.
            dynamic (boolean) : Flag that states whether the skill is dynamic.  
                If True, it will use our joint impedance controller and sensor values.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            k_gains (list): List of 7 floats corresponding to the k_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default k_gains.
            d_gains (list): List of 7 floats corresponding to the d_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default d_gains.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            ignore_virtual_walls (boolean): Function checks for collisions with 
                virtual walls by default. If False, the robot no longer checks,
                which may be dangerous.
            skill_desc (string) : Skill description to use for logging on
                control-pc.

        Raises:
            ValueError: If is_joints_reachable(joints) returns False
        '''

        joints = np.array(joints).tolist() 

        if dynamic:
            skill = Skill(SkillType.ImpedanceControlSkill, 
                          TrajectoryGeneratorType.PassThroughJointTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.JointImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                          skill_desc=skill_desc)
            use_impedance=True
            block = False
        else:
            if use_impedance:
                skill = Skill(SkillType.ImpedanceControlSkill, 
                              TrajectoryGeneratorType.MinJerkJointTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.JointImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                              skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.JointPositionSkill, 
                              TrajectoryGeneratorType.MinJerkJointTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                              skill_desc=skill_desc)


        if not self.is_joints_reachable(joints):
            raise ValueError('Joints not reachable!')

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)

        skill.set_joint_impedances(use_impedance, cartesian_impedances, joint_impedances, k_gains, d_gains)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            if dynamic:
                skill.add_time_termination_params(buffer_time)
            else:
                skill.add_joint_threshold_params(buffer_time, FC.DEFAULT_JOINT_THRESHOLDS)

        skill.add_goal_joints(duration, joints)
        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

        if dynamic:
            sleep(FC.DYNAMIC_SKILL_WAIT_TIME)

    def apply_joint_torques(self, torques, duration, ignore_errors=True, skill_desc='',):
        '''Commands Arm to apply given joint torques for duration seconds

        Args:
            torques (list): A list of 7 numbers that correspond to torques in Nm.
            duration (float): A float in the unit of seconds
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''
        pass

    def execute_joint_dmp(self, 
                          joint_dmp_info, 
                          duration, 
                          initial_sensor_values=None,
                          use_impedance=False, 
                          buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                          force_thresholds=None,
                          torque_thresholds=None,
                          cartesian_impedances=None,
                          joint_impedances=None, 
                          k_gains=None, 
                          d_gains=None, 
                          block=True, 
                          ignore_errors=True,
                          skill_desc='JointDmp'):
        '''Commands Arm to execute a given joint dmp

        Args:
            joint_dmp_info (dict): Contains all the parameters of a joint DMP
                (tau, alpha, beta, num_basis, num_sensors, mu, h, and weights)
            duration (float): A float in the unit of seconds
            initial_sensor_values (list): List of initial sensor values.
                If None it will default to ones.
            use_impedance (boolean) : Function uses the Franka joint impedance  
                controller by default. If True, uses our joint impedance controller.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            k_gains (list): List of 7 floats corresponding to the k_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default k_gains.
            d_gains (list): List of 7 floats corresponding to the d_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default d_gains.
            block (boolean) : Function blocks by default. If False, the function 
                becomes asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''

        if use_impedance:
            skill = Skill(SkillType.ImpedanceControlSkill, 
                          TrajectoryGeneratorType.JointDmpTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.JointImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                          skill_desc=skill_desc)
        else:
            skill = Skill(SkillType.JointPositionSkill, 
                          TrajectoryGeneratorType.JointDmpTrajectoryGenerator,
                          feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                          termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                          skill_desc=skill_desc)

        if initial_sensor_values is None:
            initial_sensor_values = np.ones(joint_dmp_info['num_sensors']).tolist()

        skill.add_initial_sensor_values(initial_sensor_values)  # sensor values
        
        skill.add_joint_dmp_params(duration, joint_dmp_info, initial_sensor_values)
        
        skill.set_joint_impedances(use_impedance, cartesian_impedances, joint_impedances, k_gains, d_gains)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

    def execute_pose_dmp(self, 
                         pose_dmp_info, 
                         duration, 
                         use_goal_formulation=False,
                         initial_sensor_values=None,
                         orientation_only = False,
                         position_only = False,
                         ee_frame = False,
                         use_impedance=True, 
                         buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                         force_thresholds=None,
                         torque_thresholds=None,
                         cartesian_impedances=None,
                         joint_impedances=None, 
                         block=True, 
                         ignore_errors=True,
                         skill_desc='PoseDmp'):
        '''Commands Arm to execute a given pose dmp

        Args:
            pose_dmp_info (dict): Contains all the parameters of a pose DMP
                (tau, alpha, beta, num_basis, num_sensors, mu, h, and weights)
            duration (float): A float in the unit of seconds
            use_goal_formulation (boolean) : Flag that represents whether to use
                the explicit goal pose dmp formulation.
            initial_sensor_values (list): List of initial sensor values.
                If None it will default to ones.
            orientation_only (boolean) : Flag that represents if the dmp weights
                are to generate a dmp only for orientation.
            position_only (boolean) : Flag that represents if the dmp weights
                are to generate a dmp only for position.
            use_impedance (boolean) : Function uses our impedance controller 
                by default. If False, uses the Franka cartesian controller.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''

        if use_impedance:
            if use_goal_formulation:
                skill = Skill(SkillType.ImpedanceControlSkill, 
                              TrajectoryGeneratorType.GoalPoseDmpTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                              skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.ImpedanceControlSkill, 
                              TrajectoryGeneratorType.PoseDmpTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                              skill_desc=skill_desc)
        else:
            if use_goal_formulation:
                skill = Skill(SkillType.CartesianPoseSkill, 
                              TrajectoryGeneratorType.GoalPoseDmpTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                              skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.CartesianPoseSkill, 
                              TrajectoryGeneratorType.PoseDmpTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                              skill_desc=skill_desc)

        if initial_sensor_values is None:
            if orientation_only or position_only:
                initial_sensor_values = np.ones(3*pose_dmp_info['num_sensors']).tolist()
            else:
                initial_sensor_values = np.ones(6*pose_dmp_info['num_sensors']).tolist()

        skill.add_initial_sensor_values(initial_sensor_values)  # sensor values

        skill.add_pose_dmp_params(orientation_only, position_only, ee_frame, duration, pose_dmp_info, initial_sensor_values)

        skill.set_cartesian_impedances(use_impedance, cartesian_impedances, joint_impedances)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

    def apply_effector_forces_torques(self,
                                      run_duration,
                                      acc_duration,
                                      max_translation,
                                      max_rotation,
                                      forces=None,
                                      torques=None,
                                      buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                                      force_thresholds=None,
                                      torque_thresholds=None,
                                      block=True,
                                      ignore_errors=True,
                                      skill_desc='ForceTorque'):
        '''Applies the given end-effector forces and torques in N and Nm

        Args:
            run_duration (float): A float in the unit of seconds
            acc_duration (float): A float in the unit of seconds. How long to
                acc/de-acc to achieve desired force.
            max_translation (float): A float in the unit of meters. Max translation 
                before the robot deaccelerates.
            max_rotation (float): A float in the unit of rad. Max rotation 
                before the robot deaccelerates.
            forces (list): Optional (defaults to None).
                A list of 3 numbers that correspond to end-effector forces in
                    3 directions
            torques (list): Optional (defaults to None).
                A list of 3 numbers that correspond to end-effector torques in
                    3 axes
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            skill_desc (string) : Skill description to use for logging on
                control-pc.

        Raises:
            ValueError if acc_duration > 0.5*run_duration, or if forces are
                too large
        '''
        if acc_duration > 0.5 * run_duration:
            raise ValueError(
                    'acc_duration must be smaller than half of run_duration!')

        forces = [0, 0, 0] if forces is None else np.array(forces).tolist()
        torques = [0, 0, 0] if torques is None else np.array(torques).tolist()

        if np.linalg.norm(forces) * run_duration > FC.MAX_LIN_MOMENTUM:
            raise ValueError('Linear momentum magnitude exceeds safety '
                    'threshold of {}'.format(FC.MAX_LIN_MOMENTUM))
        if np.linalg.norm(torques) * run_duration > FC.MAX_ANG_MOMENTUM:
            raise ValueError('Angular momentum magnitude exceeds safety '
                    'threshold of {}'.format(FC.MAX_ANG_MOMENTUM))

        skill = Skill(SkillType.ForceTorqueSkill, 
                      TrajectoryGeneratorType.ImpulseTrajectoryGenerator,
                      feedback_controller_type=FeedbackControllerType.PassThroughFeedbackController,
                      termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                      skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)
        
        skill.add_impulse_params(run_duration, acc_duration, max_translation, max_rotation, forces, torques)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

    def apply_effector_forces_along_axis(self,
                                         run_duration,
                                         acc_duration,
                                         max_translation,
                                         forces,
                                         buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                                         force_thresholds=None,
                                         torque_thresholds=None,
                                         block=True,
                                         ignore_errors=True,
                                         skill_desc='ForcesAlongAxis'):
        '''Applies the given end-effector forces and torques in N and Nm

        Args:
            run_duration (float): A float in the unit of seconds
            acc_duration (float): A float in the unit of seconds.
                How long to acc/de-acc to achieve desired force.
            max_translation (float): A float in the unit of meters. Max 
                translation before the robot deaccelerates.
            forces (list): Optional (defaults to None).
                A list of 3 numbers that correspond to end-effector forces in
                    3 directions
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
                    
        Raises:
            ValueError if acc_duration > 0.5*run_duration, or if forces are
                too large
        '''
        if acc_duration > 0.5 * run_duration:
            raise ValueError(
                    'acc_duration must be smaller than half of run_duration!')
        if np.linalg.norm(forces) * run_duration > FC.MAX_LIN_MOMENTUM_CONSTRAINED:
            raise ValueError('Linear momentum magnitude exceeds safety ' \
                    'threshold of {}'.format(FC.MAX_LIN_MOMENTUM_CONSTRAINED))

        forces = np.array(forces)
        force_axis = forces / np.linalg.norm(forces)

        skill = Skill(SkillType.ForceTorqueSkill, 
                      TrajectoryGeneratorType.ImpulseTrajectoryGenerator,
                      feedback_controller_type=FeedbackControllerType.ForceAxisImpedenceFeedbackController,
                      termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                      skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)
        
        skill.add_impulse_params(run_duration, acc_duration, max_translation, 0, forces.tolist(), [0, 0, 0])

        skill.add_force_axis_params(FC.DEFAULT_FORCE_AXIS_TRANSLATIONAL_STIFFNESS,
                                    FC.DEFAULT_FORCE_AXIS_ROTATIONAL_STIFFNESS,
                                    force_axis.tolist())

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

    def goto_gripper(self, 
                     width, 
                     grasp=False, 
                     speed=0.04, 
                     force=0.0, 
                     block=True, 
                     ignore_errors=True, 
                     skill_desc='GoToGripper'):
        '''Commands gripper to goto a certain width, applying up to the given
            (default is max) force if needed

        Args:
            width (float): A float in the unit of meters
            grasp (boolean): Flag that signals whether to grasp
            speed (float): Gripper operation speed in meters per sec
            force (float): Max gripper force to apply in N. Default to None,
                which gives acceptable force
            block (boolean) : Function blocks by default. If False, the function 
                becomes asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            skill_desc (string) : Skill description to use for logging on
                control-pc.

        Raises:
            ValueError: If width is less than 0 or greater than TODO(jacky)
                the maximum gripper opening
        '''
        skill = Skill(SkillType.GripperSkill, 
                      TrajectoryGeneratorType.GripperTrajectoryGenerator, 
                      skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)

        skill.add_gripper_params(grasp, width, speed, force)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)
        # this is so the gripper state can be updated, which happens with a
        # small lag
        sleep(FC.GRIPPER_CMD_SLEEP_TIME)

    def selective_guidance_mode(self, 
                                duration=5,
                                use_joints=False, 
                                use_impedance=False,
                                use_ee_frame=False,
                                buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                                force_thresholds=None,
                                torque_thresholds=None,
                                cartesian_impedances=None,
                                joint_impedances=None,
                                k_gains=None,
                                d_gains=None,
                                block=True,
                                ignore_errors=True,
                                ignore_virtual_walls=False,
                                skill_desc='SelectiveGuidance'):
        '''Commands the Arm to stay in its current position with selective impedances
        that allow guidance in either certain joints or in cartesian pose.

        Args:
            duration (float): How much time this guidance should take
            use_joints (boolean) : Function uses cartesian impedance  
                controller by default. If True, it uses joint impedance.
            use_impedance (boolean) : Function uses the Franka joint impedance  
                controller by default. If True, uses our joint impedance controller.
            use_ee_frame (boolean) : Function uses the end-effector cartesian feedback
                controller only when use_impedance is True.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            cartesian impedances (list): List of 6 floats corresponding to
                impedances on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will use default impedances.
            joint impedances (list): List of 7 floats corresponding to
                impedances on each joint. This is used when use_impedance is 
                False. Default is None. If None then will use default impedances.
            k_gains (list): List of 7 floats corresponding to the k_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default k_gains.
            d_gains (list): List of 7 floats corresponding to the d_gains on each joint
                for our impedance controller. This is used when use_impedance is 
                True. Default is None. If None then will use default d_gains.
            block (boolean) : Function blocks by default. If False, the function becomes
                asynchronous and can be preempted.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            ignore_virtual_walls (boolean): Function checks for collisions with 
                virtual walls by default. If False, the robot no longer checks,
                which may be dangerous.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''
        if use_joints:
            if use_impedance:
                skill = Skill(SkillType.ImpedanceControlSkill, 
                              TrajectoryGeneratorType.StayInInitialJointsTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.JointImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                              skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.JointPositionSkill, 
                              TrajectoryGeneratorType.StayInInitialJointsTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.FinalJointTerminationHandler, 
                              skill_desc=skill_desc)
        else:
            if use_impedance:
                if use_ee_frame:
                    skill = Skill(SkillType.ImpedanceControlSkill, 
                                  TrajectoryGeneratorType.StayInInitialPoseTrajectoryGenerator,
                                  feedback_controller_type=FeedbackControllerType.EECartesianImpedanceFeedbackController,
                                  termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                                  skill_desc=skill_desc)
                else:
                    skill = Skill(SkillType.ImpedanceControlSkill, 
                                  TrajectoryGeneratorType.StayInInitialPoseTrajectoryGenerator,
                                  feedback_controller_type=FeedbackControllerType.CartesianImpedanceFeedbackController,
                                  termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                                  skill_desc=skill_desc)
            else:
                skill = Skill(SkillType.CartesianPoseSkill, 
                              TrajectoryGeneratorType.StayInInitialPoseTrajectoryGenerator,
                              feedback_controller_type=FeedbackControllerType.SetInternalImpedanceFeedbackController,
                              termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                              skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)
        
        skill.add_run_time(duration)

        if use_joints:
            skill.set_joint_impedances(use_impedance, cartesian_impedances, joint_impedances, k_gains, d_gains)
        else:
            skill.set_cartesian_impedances(use_impedance, cartesian_impedances, joint_impedances)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)

        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=block,
                        ignore_errors=ignore_errors)

    def open_gripper(self, block=True, skill_desc='OpenGripper'):
        '''Opens gripper to maximum width
        '''
        self.goto_gripper(FC.GRIPPER_WIDTH_MAX, block=block, skill_desc=skill_desc)

    def close_gripper(self, grasp=True, block=True, skill_desc='CloseGripper'):
        '''Closes the gripper as much as possible
        '''
        self.goto_gripper(FC.GRIPPER_WIDTH_MIN, grasp=grasp,
                          force=FC.GRIPPER_MAX_FORCE if grasp else None,
                          block=block, skill_desc=skill_desc)

    def run_guide_mode(self, duration=10, block=True, skill_desc='GuideMode'):
        self.apply_effector_forces_torques(duration, 0, 0, 0, block=block, skill_desc=skill_desc)

    def run_dynamic_force_position(self,
                  duration=3,
                  buffer_time=FC.DEFAULT_TERM_BUFFER_TIME,
                  force_thresholds=None,
                  torque_thresholds=None,
                  position_kps_cart=FC.DEFAULT_TRANSLATIONAL_STIFFNESSES + FC.DEFAULT_ROTATIONAL_STIFFNESSES,
                  force_kps_cart=FC.DEFAULT_HFPC_FORCE_GAIN,
                  position_kps_joint=FC.DEFAULT_K_GAINS,
                  force_kps_joint=FC.DEFAULT_HFPC_FORCE_GAIN,
                  S=FC.DEFAULT_HFPC_S,
                  interpolate=False,
                  use_cartesian_gains=True,
                  ignore_errors=True,
                  ignore_virtual_walls=False,
                  skill_desc=''):
        '''Commands Arm to run dynamic hybrid force position control

        Args:
            duration (float) : How much time this robot motion should take
            use_impedance (boolean) : Function uses our impedance controller 
                by default. If False, uses the Franka cartesian controller.
            buffer_time (float): How much extra time the termination handler will wait
                before stopping the skill after duration has passed.
            force_thresholds (list): List of 6 floats corresponding to
                force limits on translation (xyz) and rotation about (xyz) axes.
                Default is None. If None then will not stop on contact.
            torque_thresholds (list): List of 7 floats corresponding to
                torque limits on each joint. Default is None. If None then will
                not stop on contact.
            position_kp_cart (list): List of 6 floats corresponding to 
                proportional gain used for position errors in cartesian space.
            force_kp_cart (list): List of 6 floats corresponding to 
                proportional gain used for force errors in cartesian space.
            position_kp_joint (list): List of 7 floats corresponding to 
                proportional gain used for position errors in joint space.
            force_kp_joint (list): List of 6 floats corresponding to 
                proportional gain used for force errors in joint space.
            S (list): List of 6 numbers between 0 and 1 for the HFPC selection matrix.
            interpolate (boolean): Whether or not to perform linear interpolation
                in between way points.
            use_cartesian_gains (boolean): Whether to use cartesian gains or
                joint gains.
            ignore_errors (boolean) : Function ignores errors by default. 
                If False, errors and some exceptions can be thrown.
            ignore_virtual_walls (boolean): Function checks for collisions with 
                virtual walls by default. If False, the robot no longer checks,
                which may be dangerous.
            skill_desc (string) : Skill description to use for logging on
                control-pc.
        '''
        if interpolate:
            traj_gen = TrajectoryGeneratorType.LinearForcePositionTrajectoryGenerator
        else:
            traj_gen = TrajectoryGeneratorType.PassThroughForcePositionTrajectoryGenerator
        skill = Skill(SkillType.ForceTorqueSkill, 
                        traj_gen,
                        feedback_controller_type=FeedbackControllerType.ForcePositionFeedbackController,
                        termination_handler_type=TerminationHandlerType.TimeTerminationHandler, 
                        skill_desc=skill_desc)

        skill.add_initial_sensor_values(FC.EMPTY_SENSOR_VALUES)
        skill.add_force_position_params(position_kps_cart, force_kps_cart, position_kps_joint, force_kps_joint, S, use_cartesian_gains)
        skill.add_run_time(duration)

        if not skill.check_for_contact_params(buffer_time, force_thresholds, torque_thresholds):
            skill.add_time_termination_params(buffer_time)
            
        goal = skill.create_goal()

        self._send_goal(goal,
                        cb=lambda x: skill.feedback_callback(x),
                        block=False,
                        ignore_errors=ignore_errors)

        sleep(FC.DYNAMIC_SKILL_WAIT_TIME)

    '''
    Reads
    '''

    def get_robot_state(self):
        '''
        Returns:
            dict of full robot state data
        '''
        return self._state_client.get_data()

    def get_pose(self):
        '''
        Returns:
            pose (RigidTransform) of the current end-effector
        '''
        tool_base_pose = self._state_client.get_pose()

        tool_pose = tool_base_pose * self._tool_delta_pose

        return tool_pose

    def get_joints(self):
        '''
        Returns:
            ndarray of shape (7,) of joint angles in radians
        '''
        return self._state_client.get_joints()

    def get_joint_torques(self):
        '''
        Returns:
            ndarray of shape (7,) of joint torques in Nm
        '''
        return self._state_client.get_joint_torques()

    def get_joint_velocities(self):
        '''
        Returns:
            ndarray of shape (7,) of joint velocities in rads/s
        '''
        return self._state_client.get_joint_velocities()

    def get_gripper_width(self):
        '''
        Returns:
            float of gripper width in meters
        '''
        return self._state_client.get_gripper_width()

    def get_gripper_is_grasped(self):
        '''
        Returns:
            True if gripper is grasping something. False otherwise
        '''
        return self._state_client.get_gripper_is_grasped()

    def get_speed(self, speed):
        '''
        Returns:
            float of current target speed parameter
        '''
        pass

    def get_tool_base_pose(self):
        '''
        Returns:
            RigidTransform of current tool base pose
        '''
        return self._tool_delta_pose.copy()

    def get_ee_force_torque(self):
        return self._state_client.get_ee_force_torque()

    '''
    Sets
    '''

    def set_tool_delta_pose(self, tool_delta_pose):
        '''Sets the tool pose relative to the end-effector pose

        Args:
            tool_delta_pose (RigidTransform)
        '''
        if tool_delta_pose.from_frame != 'franka_tool' \
                or tool_delta_pose.to_frame != 'franka_tool_base':
            raise ValueError('tool_delta_pose has invalid frame names! ' \
                             'Make sure it has from_frame=franka_tool, and ' \
                             'to_frame=franka_tool_base')

        self._tool_delta_pose = tool_delta_pose.copy()

    def set_speed(self, speed):
        '''Sets current target speed parameter

        Args:
            speed (float)
        '''
        pass


    '''
    Forward Kinematics, Jacobian, other offline methods that were removed for class purposes
    '''


    def publish_joints(self, joints=None):
        ''' Publish the Franka joints to ROS

        Args:
            joints (list): Optional: Defaults to None
                            A list of 7 numbers that correspond to to the joint angles in radians
                            If None, will use current real robot joints.
        '''
        if joints is None:
            joints = self.get_joints()
                        
        joint_state = JointState()
        joint_state.name = FC.JOINT_NAMES
        joint_state.header.stamp = rospy.Time.now()

        if len(joints) == 7:
            joints = np.concatenate([joints, [0, 0]])
        joint_state.position = joints

        self._joint_state_pub.publish(joint_state)

    '''
    Misc
    '''
    def reset_joints(self, duration=5, skill_desc='', block=True, ignore_errors=True):
        '''Commands Arm to goto hardcoded home joint configuration
        '''
        self.goto_joints(FC.HOME_JOINTS, duration=duration, skill_desc=skill_desc, block=block, ignore_errors=ignore_errors)

    def reset_pose(self, duration=5, skill_desc='', block=True, ignore_errors=True):
        '''Commands Arm to goto hardcoded home pose
        '''
        self.goto_pose(FC.HOME_POSE, duration=duration, skill_desc=skill_desc, block=block, ignore_errors=ignore_errors)

    def is_joints_reachable(self, joints):
        '''
        Returns:
            True if all joints within joint limits
        '''
        for i, val in enumerate(joints):
            if val <= FC.JOINT_LIMITS_MIN[i] or val >= FC.JOINT_LIMITS_MAX[i]:
                return False

        return True
