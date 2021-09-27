# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from franka_interface_msgs/ExecuteSkillActionGoal.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct

import actionlib_msgs.msg
import franka_interface_msgs.msg
import genpy
import std_msgs.msg

class ExecuteSkillActionGoal(genpy.Message):
  _md5sum = "9010c44dae6748cc80ceac2c2cce6e13"
  _type = "franka_interface_msgs/ExecuteSkillActionGoal"
  _has_header = True  # flag to mark the presence of a Header object
  _full_text = """# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======

Header header
actionlib_msgs/GoalID goal_id
ExecuteSkillGoal goal

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: actionlib_msgs/GoalID
# The stamp should store the time at which this goal was requested.
# It is used by an action server when it tries to preempt all
# goals that were requested before a certain time
time stamp

# The id provides a way to associate feedback and
# result message with specific goal requests. The id
# specified must be unique.
string id


================================================================================
MSG: franka_interface_msgs/ExecuteSkillGoal
# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======
uint8 skill_type
string skill_description
uint8 meta_skill_type
int64 meta_skill_id

# Sensor topic to subscribe to
string[] sensor_topics
uint64[] sensor_value_sizes
float64[] initial_sensor_values

# traj gen
uint8 trajectory_generator_type
int32 trajectory_generator_param_data_size
uint8[] trajectory_generator_param_data

# fbc
uint8 feedback_controller_type
int32 feedback_controller_param_data_size
uint8[] feedback_controller_param_data

# termination
uint8 termination_handler_type
int32 termination_handler_param_data_size
uint8[] termination_handler_param_data 

# timer
uint8 timer_type
int32 num_timer_params
uint8[] timer_params
"""
  __slots__ = ['header','goal_id','goal']
  _slot_types = ['std_msgs/Header','actionlib_msgs/GoalID','franka_interface_msgs/ExecuteSkillGoal']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       header,goal_id,goal

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(ExecuteSkillActionGoal, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.header is None:
        self.header = std_msgs.msg.Header()
      if self.goal_id is None:
        self.goal_id = actionlib_msgs.msg.GoalID()
      if self.goal is None:
        self.goal = franka_interface_msgs.msg.ExecuteSkillGoal()
    else:
      self.header = std_msgs.msg.Header()
      self.goal_id = actionlib_msgs.msg.GoalID()
      self.goal = franka_interface_msgs.msg.ExecuteSkillGoal()

  def _get_types(self):
    """
    internal API method
    """
    return self._slot_types

  def serialize(self, buff):
    """
    serialize message into buffer
    :param buff: buffer, ``StringIO``
    """
    try:
      _x = self
      buff.write(_get_struct_3I().pack(_x.header.seq, _x.header.stamp.secs, _x.header.stamp.nsecs))
      _x = self.header.frame_id
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_2I().pack(_x.goal_id.stamp.secs, _x.goal_id.stamp.nsecs))
      _x = self.goal_id.id
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self.goal.skill_type
      buff.write(_get_struct_B().pack(_x))
      _x = self.goal.skill_description
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bq().pack(_x.goal.meta_skill_type, _x.goal.meta_skill_id))
      length = len(self.goal.sensor_topics)
      buff.write(_struct_I.pack(length))
      for val1 in self.goal.sensor_topics:
        length = len(val1)
        if python3 or type(val1) == unicode:
          val1 = val1.encode('utf-8')
          length = len(val1)
        buff.write(struct.Struct('<I%ss'%length).pack(length, val1))
      length = len(self.goal.sensor_value_sizes)
      buff.write(_struct_I.pack(length))
      pattern = '<%sQ'%length
      buff.write(struct.Struct(pattern).pack(*self.goal.sensor_value_sizes))
      length = len(self.goal.initial_sensor_values)
      buff.write(_struct_I.pack(length))
      pattern = '<%sd'%length
      buff.write(struct.Struct(pattern).pack(*self.goal.initial_sensor_values))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.trajectory_generator_type, _x.goal.trajectory_generator_param_data_size))
      _x = self.goal.trajectory_generator_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.feedback_controller_type, _x.goal.feedback_controller_param_data_size))
      _x = self.goal.feedback_controller_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.termination_handler_type, _x.goal.termination_handler_param_data_size))
      _x = self.goal.termination_handler_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.timer_type, _x.goal.num_timer_params))
      _x = self.goal.timer_params
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize(self, str):
    """
    unpack serialized message in str into this message instance
    :param str: byte array of serialized message, ``str``
    """
    codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      if self.header is None:
        self.header = std_msgs.msg.Header()
      if self.goal_id is None:
        self.goal_id = actionlib_msgs.msg.GoalID()
      if self.goal is None:
        self.goal = franka_interface_msgs.msg.ExecuteSkillGoal()
      end = 0
      _x = self
      start = end
      end += 12
      (_x.header.seq, _x.header.stamp.secs, _x.header.stamp.nsecs,) = _get_struct_3I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.header.frame_id = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.header.frame_id = str[start:end]
      _x = self
      start = end
      end += 8
      (_x.goal_id.stamp.secs, _x.goal_id.stamp.nsecs,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.goal_id.id = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.goal_id.id = str[start:end]
      start = end
      end += 1
      (self.goal.skill_type,) = _get_struct_B().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.goal.skill_description = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.goal.skill_description = str[start:end]
      _x = self
      start = end
      end += 9
      (_x.goal.meta_skill_type, _x.goal.meta_skill_id,) = _get_struct_Bq().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.goal.sensor_topics = []
      for i in range(0, length):
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1 = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1 = str[start:end]
        self.goal.sensor_topics.append(val1)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sQ'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.goal.sensor_value_sizes = s.unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sd'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.goal.initial_sensor_values = s.unpack(str[start:end])
      _x = self
      start = end
      end += 5
      (_x.goal.trajectory_generator_type, _x.goal.trajectory_generator_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.trajectory_generator_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.feedback_controller_type, _x.goal.feedback_controller_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.feedback_controller_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.termination_handler_type, _x.goal.termination_handler_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.termination_handler_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.timer_type, _x.goal.num_timer_params,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.timer_params = str[start:end]
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill


  def serialize_numpy(self, buff, numpy):
    """
    serialize message with numpy array types into buffer
    :param buff: buffer, ``StringIO``
    :param numpy: numpy python module
    """
    try:
      _x = self
      buff.write(_get_struct_3I().pack(_x.header.seq, _x.header.stamp.secs, _x.header.stamp.nsecs))
      _x = self.header.frame_id
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_2I().pack(_x.goal_id.stamp.secs, _x.goal_id.stamp.nsecs))
      _x = self.goal_id.id
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self.goal.skill_type
      buff.write(_get_struct_B().pack(_x))
      _x = self.goal.skill_description
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bq().pack(_x.goal.meta_skill_type, _x.goal.meta_skill_id))
      length = len(self.goal.sensor_topics)
      buff.write(_struct_I.pack(length))
      for val1 in self.goal.sensor_topics:
        length = len(val1)
        if python3 or type(val1) == unicode:
          val1 = val1.encode('utf-8')
          length = len(val1)
        buff.write(struct.Struct('<I%ss'%length).pack(length, val1))
      length = len(self.goal.sensor_value_sizes)
      buff.write(_struct_I.pack(length))
      pattern = '<%sQ'%length
      buff.write(self.goal.sensor_value_sizes.tostring())
      length = len(self.goal.initial_sensor_values)
      buff.write(_struct_I.pack(length))
      pattern = '<%sd'%length
      buff.write(self.goal.initial_sensor_values.tostring())
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.trajectory_generator_type, _x.goal.trajectory_generator_param_data_size))
      _x = self.goal.trajectory_generator_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.feedback_controller_type, _x.goal.feedback_controller_param_data_size))
      _x = self.goal.feedback_controller_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.termination_handler_type, _x.goal.termination_handler_param_data_size))
      _x = self.goal.termination_handler_param_data
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self
      buff.write(_get_struct_Bi().pack(_x.goal.timer_type, _x.goal.num_timer_params))
      _x = self.goal.timer_params
      length = len(_x)
      # - if encoded as a list instead, serialize as bytes instead of string
      if type(_x) in [list, tuple]:
        buff.write(struct.Struct('<I%sB'%length).pack(length, *_x))
      else:
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize_numpy(self, str, numpy):
    """
    unpack serialized message in str into this message instance using numpy for array types
    :param str: byte array of serialized message, ``str``
    :param numpy: numpy python module
    """
    codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      if self.header is None:
        self.header = std_msgs.msg.Header()
      if self.goal_id is None:
        self.goal_id = actionlib_msgs.msg.GoalID()
      if self.goal is None:
        self.goal = franka_interface_msgs.msg.ExecuteSkillGoal()
      end = 0
      _x = self
      start = end
      end += 12
      (_x.header.seq, _x.header.stamp.secs, _x.header.stamp.nsecs,) = _get_struct_3I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.header.frame_id = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.header.frame_id = str[start:end]
      _x = self
      start = end
      end += 8
      (_x.goal_id.stamp.secs, _x.goal_id.stamp.nsecs,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.goal_id.id = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.goal_id.id = str[start:end]
      start = end
      end += 1
      (self.goal.skill_type,) = _get_struct_B().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.goal.skill_description = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.goal.skill_description = str[start:end]
      _x = self
      start = end
      end += 9
      (_x.goal.meta_skill_type, _x.goal.meta_skill_id,) = _get_struct_Bq().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.goal.sensor_topics = []
      for i in range(0, length):
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1 = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1 = str[start:end]
        self.goal.sensor_topics.append(val1)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sQ'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.goal.sensor_value_sizes = numpy.frombuffer(str[start:end], dtype=numpy.uint64, count=length)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sd'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.goal.initial_sensor_values = numpy.frombuffer(str[start:end], dtype=numpy.float64, count=length)
      _x = self
      start = end
      end += 5
      (_x.goal.trajectory_generator_type, _x.goal.trajectory_generator_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.trajectory_generator_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.feedback_controller_type, _x.goal.feedback_controller_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.feedback_controller_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.termination_handler_type, _x.goal.termination_handler_param_data_size,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.termination_handler_param_data = str[start:end]
      _x = self
      start = end
      end += 5
      (_x.goal.timer_type, _x.goal.num_timer_params,) = _get_struct_Bi().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      self.goal.timer_params = str[start:end]
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill

_struct_I = genpy.struct_I
def _get_struct_I():
    global _struct_I
    return _struct_I
_struct_2I = None
def _get_struct_2I():
    global _struct_2I
    if _struct_2I is None:
        _struct_2I = struct.Struct("<2I")
    return _struct_2I
_struct_3I = None
def _get_struct_3I():
    global _struct_3I
    if _struct_3I is None:
        _struct_3I = struct.Struct("<3I")
    return _struct_3I
_struct_B = None
def _get_struct_B():
    global _struct_B
    if _struct_B is None:
        _struct_B = struct.Struct("<B")
    return _struct_B
_struct_Bi = None
def _get_struct_Bi():
    global _struct_Bi
    if _struct_Bi is None:
        _struct_Bi = struct.Struct("<Bi")
    return _struct_Bi
_struct_Bq = None
def _get_struct_Bq():
    global _struct_Bq
    if _struct_Bq is None:
        _struct_Bq = struct.Struct("<Bq")
    return _struct_Bq
