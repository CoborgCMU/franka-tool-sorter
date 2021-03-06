; Auto-generated. Do not edit!


(cl:in-package franka_interface_msgs-msg)


;//! \htmlinclude ExecuteSkillActionGoal.msg.html

(cl:defclass <ExecuteSkillActionGoal> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (goal_id
    :reader goal_id
    :initarg :goal_id
    :type actionlib_msgs-msg:GoalID
    :initform (cl:make-instance 'actionlib_msgs-msg:GoalID))
   (goal
    :reader goal
    :initarg :goal
    :type franka_interface_msgs-msg:ExecuteSkillGoal
    :initform (cl:make-instance 'franka_interface_msgs-msg:ExecuteSkillGoal)))
)

(cl:defclass ExecuteSkillActionGoal (<ExecuteSkillActionGoal>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ExecuteSkillActionGoal>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ExecuteSkillActionGoal)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name franka_interface_msgs-msg:<ExecuteSkillActionGoal> is deprecated: use franka_interface_msgs-msg:ExecuteSkillActionGoal instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <ExecuteSkillActionGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader franka_interface_msgs-msg:header-val is deprecated.  Use franka_interface_msgs-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'goal_id-val :lambda-list '(m))
(cl:defmethod goal_id-val ((m <ExecuteSkillActionGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader franka_interface_msgs-msg:goal_id-val is deprecated.  Use franka_interface_msgs-msg:goal_id instead.")
  (goal_id m))

(cl:ensure-generic-function 'goal-val :lambda-list '(m))
(cl:defmethod goal-val ((m <ExecuteSkillActionGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader franka_interface_msgs-msg:goal-val is deprecated.  Use franka_interface_msgs-msg:goal instead.")
  (goal m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ExecuteSkillActionGoal>) ostream)
  "Serializes a message object of type '<ExecuteSkillActionGoal>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'goal_id) ostream)
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'goal) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ExecuteSkillActionGoal>) istream)
  "Deserializes a message object of type '<ExecuteSkillActionGoal>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'goal_id) istream)
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'goal) istream)
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ExecuteSkillActionGoal>)))
  "Returns string type for a message object of type '<ExecuteSkillActionGoal>"
  "franka_interface_msgs/ExecuteSkillActionGoal")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ExecuteSkillActionGoal)))
  "Returns string type for a message object of type 'ExecuteSkillActionGoal"
  "franka_interface_msgs/ExecuteSkillActionGoal")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ExecuteSkillActionGoal>)))
  "Returns md5sum for a message object of type '<ExecuteSkillActionGoal>"
  "9010c44dae6748cc80ceac2c2cce6e13")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ExecuteSkillActionGoal)))
  "Returns md5sum for a message object of type 'ExecuteSkillActionGoal"
  "9010c44dae6748cc80ceac2c2cce6e13")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ExecuteSkillActionGoal>)))
  "Returns full string definition for message of type '<ExecuteSkillActionGoal>"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%Header header~%actionlib_msgs/GoalID goal_id~%ExecuteSkillGoal goal~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: actionlib_msgs/GoalID~%# The stamp should store the time at which this goal was requested.~%# It is used by an action server when it tries to preempt all~%# goals that were requested before a certain time~%time stamp~%~%# The id provides a way to associate feedback and~%# result message with specific goal requests. The id~%# specified must be unique.~%string id~%~%~%================================================================================~%MSG: franka_interface_msgs/ExecuteSkillGoal~%# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%uint8 skill_type~%string skill_description~%uint8 meta_skill_type~%int64 meta_skill_id~%~%# Sensor topic to subscribe to~%string[] sensor_topics~%uint64[] sensor_value_sizes~%float64[] initial_sensor_values~%~%# traj gen~%uint8 trajectory_generator_type~%int32 trajectory_generator_param_data_size~%uint8[] trajectory_generator_param_data~%~%# fbc~%uint8 feedback_controller_type~%int32 feedback_controller_param_data_size~%uint8[] feedback_controller_param_data~%~%# termination~%uint8 termination_handler_type~%int32 termination_handler_param_data_size~%uint8[] termination_handler_param_data ~%~%# timer~%uint8 timer_type~%int32 num_timer_params~%uint8[] timer_params~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ExecuteSkillActionGoal)))
  "Returns full string definition for message of type 'ExecuteSkillActionGoal"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%Header header~%actionlib_msgs/GoalID goal_id~%ExecuteSkillGoal goal~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: actionlib_msgs/GoalID~%# The stamp should store the time at which this goal was requested.~%# It is used by an action server when it tries to preempt all~%# goals that were requested before a certain time~%time stamp~%~%# The id provides a way to associate feedback and~%# result message with specific goal requests. The id~%# specified must be unique.~%string id~%~%~%================================================================================~%MSG: franka_interface_msgs/ExecuteSkillGoal~%# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%uint8 skill_type~%string skill_description~%uint8 meta_skill_type~%int64 meta_skill_id~%~%# Sensor topic to subscribe to~%string[] sensor_topics~%uint64[] sensor_value_sizes~%float64[] initial_sensor_values~%~%# traj gen~%uint8 trajectory_generator_type~%int32 trajectory_generator_param_data_size~%uint8[] trajectory_generator_param_data~%~%# fbc~%uint8 feedback_controller_type~%int32 feedback_controller_param_data_size~%uint8[] feedback_controller_param_data~%~%# termination~%uint8 termination_handler_type~%int32 termination_handler_param_data_size~%uint8[] termination_handler_param_data ~%~%# timer~%uint8 timer_type~%int32 num_timer_params~%uint8[] timer_params~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ExecuteSkillActionGoal>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'goal_id))
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'goal))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ExecuteSkillActionGoal>))
  "Converts a ROS message object to a list"
  (cl:list 'ExecuteSkillActionGoal
    (cl:cons ':header (header msg))
    (cl:cons ':goal_id (goal_id msg))
    (cl:cons ':goal (goal msg))
))
