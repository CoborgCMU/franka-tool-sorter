# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: termination_handler_params_msg.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='termination_handler_params_msg.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n$termination_handler_params_msg.proto\"l\n ContactTerminationHandlerMessage\x12\x13\n\x0b\x62uffer_time\x18\x01 \x02(\x01\x12\x18\n\x10\x66orce_thresholds\x18\x02 \x03(\x01\x12\x19\n\x11torque_thresholds\x18\x03 \x03(\x01\"F\n\x15JointThresholdMessage\x12\x13\n\x0b\x62uffer_time\x18\x01 \x02(\x01\x12\x18\n\x10joint_thresholds\x18\x02 \x03(\x01\"h\n\x14PoseThresholdMessage\x12\x13\n\x0b\x62uffer_time\x18\x01 \x02(\x01\x12\x1b\n\x13position_thresholds\x18\x02 \x03(\x01\x12\x1e\n\x16orientation_thresholds\x18\x03 \x03(\x01\"4\n\x1dTimeTerminationHandlerMessage\x12\x13\n\x0b\x62uffer_time\x18\x01 \x02(\x01'
)




_CONTACTTERMINATIONHANDLERMESSAGE = _descriptor.Descriptor(
  name='ContactTerminationHandlerMessage',
  full_name='ContactTerminationHandlerMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='buffer_time', full_name='ContactTerminationHandlerMessage.buffer_time', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='force_thresholds', full_name='ContactTerminationHandlerMessage.force_thresholds', index=1,
      number=2, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='torque_thresholds', full_name='ContactTerminationHandlerMessage.torque_thresholds', index=2,
      number=3, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=40,
  serialized_end=148,
)


_JOINTTHRESHOLDMESSAGE = _descriptor.Descriptor(
  name='JointThresholdMessage',
  full_name='JointThresholdMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='buffer_time', full_name='JointThresholdMessage.buffer_time', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='joint_thresholds', full_name='JointThresholdMessage.joint_thresholds', index=1,
      number=2, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=150,
  serialized_end=220,
)


_POSETHRESHOLDMESSAGE = _descriptor.Descriptor(
  name='PoseThresholdMessage',
  full_name='PoseThresholdMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='buffer_time', full_name='PoseThresholdMessage.buffer_time', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='position_thresholds', full_name='PoseThresholdMessage.position_thresholds', index=1,
      number=2, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='orientation_thresholds', full_name='PoseThresholdMessage.orientation_thresholds', index=2,
      number=3, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=222,
  serialized_end=326,
)


_TIMETERMINATIONHANDLERMESSAGE = _descriptor.Descriptor(
  name='TimeTerminationHandlerMessage',
  full_name='TimeTerminationHandlerMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='buffer_time', full_name='TimeTerminationHandlerMessage.buffer_time', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=328,
  serialized_end=380,
)

DESCRIPTOR.message_types_by_name['ContactTerminationHandlerMessage'] = _CONTACTTERMINATIONHANDLERMESSAGE
DESCRIPTOR.message_types_by_name['JointThresholdMessage'] = _JOINTTHRESHOLDMESSAGE
DESCRIPTOR.message_types_by_name['PoseThresholdMessage'] = _POSETHRESHOLDMESSAGE
DESCRIPTOR.message_types_by_name['TimeTerminationHandlerMessage'] = _TIMETERMINATIONHANDLERMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ContactTerminationHandlerMessage = _reflection.GeneratedProtocolMessageType('ContactTerminationHandlerMessage', (_message.Message,), {
  'DESCRIPTOR' : _CONTACTTERMINATIONHANDLERMESSAGE,
  '__module__' : 'termination_handler_params_msg_pb2'
  # @@protoc_insertion_point(class_scope:ContactTerminationHandlerMessage)
  })
_sym_db.RegisterMessage(ContactTerminationHandlerMessage)

JointThresholdMessage = _reflection.GeneratedProtocolMessageType('JointThresholdMessage', (_message.Message,), {
  'DESCRIPTOR' : _JOINTTHRESHOLDMESSAGE,
  '__module__' : 'termination_handler_params_msg_pb2'
  # @@protoc_insertion_point(class_scope:JointThresholdMessage)
  })
_sym_db.RegisterMessage(JointThresholdMessage)

PoseThresholdMessage = _reflection.GeneratedProtocolMessageType('PoseThresholdMessage', (_message.Message,), {
  'DESCRIPTOR' : _POSETHRESHOLDMESSAGE,
  '__module__' : 'termination_handler_params_msg_pb2'
  # @@protoc_insertion_point(class_scope:PoseThresholdMessage)
  })
_sym_db.RegisterMessage(PoseThresholdMessage)

TimeTerminationHandlerMessage = _reflection.GeneratedProtocolMessageType('TimeTerminationHandlerMessage', (_message.Message,), {
  'DESCRIPTOR' : _TIMETERMINATIONHANDLERMESSAGE,
  '__module__' : 'termination_handler_params_msg_pb2'
  # @@protoc_insertion_point(class_scope:TimeTerminationHandlerMessage)
  })
_sym_db.RegisterMessage(TimeTerminationHandlerMessage)


# @@protoc_insertion_point(module_scope)
