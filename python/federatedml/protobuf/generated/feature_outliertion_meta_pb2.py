# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: feature-outliertion-meta.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='feature-outliertion-meta.proto',
  package='com.webank.ai.fate.core.mlmodel.buffer',
  syntax='proto3',
  serialized_options=_b('B\033FeatureOutliertionMetaProto'),
  serialized_pb=_b('\n\x1e\x66\x65\x61ture-outliertion-meta.proto\x12&com.webank.ai.fate.core.mlmodel.buffer\"\xb8\x03\n\x12\x46\x65\x61tureOutlierMeta\x12\x12\n\nis_imputer\x18\x01 \x01(\x08\x12\x10\n\x08strategy\x18\x02 \x01(\t\x12\x63\n\rmissing_value\x18\x03 \x03(\x0b\x32L.com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.MissingValueEntry\x12\x1a\n\x12missing_value_type\x18\x04 \x03(\t\x12\x63\n\rcols_strategy\x18\x05 \x03(\x0b\x32L.com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.ColsStrategyEntry\x1a\x61\n\x11MissingValueEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12;\n\x05value\x18\x02 \x01(\x0b\x32,.com.webank.ai.fate.core.mlmodel.buffer.list:\x02\x38\x01\x1a\x33\n\x11\x43olsStrategyEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x15\n\x04list\x12\r\n\x05value\x18\x01 \x03(\x01\"|\n\x16\x46\x65\x61tureOutliertionMeta\x12P\n\x0cimputer_meta\x18\x01 \x01(\x0b\x32:.com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta\x12\x10\n\x08need_run\x18\x02 \x01(\x08\x42\x1d\x42\x1b\x46\x65\x61tureOutliertionMetaProtob\x06proto3')
)




_FEATUREOUTLIERMETA_MISSINGVALUEENTRY = _descriptor.Descriptor(
  name='MissingValueEntry',
  full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.MissingValueEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.MissingValueEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.MissingValueEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=365,
  serialized_end=462,
)

_FEATUREOUTLIERMETA_COLSSTRATEGYENTRY = _descriptor.Descriptor(
  name='ColsStrategyEntry',
  full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.ColsStrategyEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.ColsStrategyEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.ColsStrategyEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=464,
  serialized_end=515,
)

_FEATUREOUTLIERMETA = _descriptor.Descriptor(
  name='FeatureOutlierMeta',
  full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_imputer', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.is_imputer', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='strategy', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.strategy', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='missing_value', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.missing_value', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='missing_value_type', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.missing_value_type', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cols_strategy', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.cols_strategy', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FEATUREOUTLIERMETA_MISSINGVALUEENTRY, _FEATUREOUTLIERMETA_COLSSTRATEGYENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=75,
  serialized_end=515,
)


_LIST = _descriptor.Descriptor(
  name='list',
  full_name='com.webank.ai.fate.core.mlmodel.buffer.list',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='com.webank.ai.fate.core.mlmodel.buffer.list.value', index=0,
      number=1, type=1, cpp_type=5, label=3,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=517,
  serialized_end=538,
)


_FEATUREOUTLIERTIONMETA = _descriptor.Descriptor(
  name='FeatureOutliertionMeta',
  full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMeta',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='imputer_meta', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMeta.imputer_meta', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='need_run', full_name='com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMeta.need_run', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=540,
  serialized_end=664,
)

_FEATUREOUTLIERMETA_MISSINGVALUEENTRY.fields_by_name['value'].message_type = _LIST
_FEATUREOUTLIERMETA_MISSINGVALUEENTRY.containing_type = _FEATUREOUTLIERMETA
_FEATUREOUTLIERMETA_COLSSTRATEGYENTRY.containing_type = _FEATUREOUTLIERMETA
_FEATUREOUTLIERMETA.fields_by_name['missing_value'].message_type = _FEATUREOUTLIERMETA_MISSINGVALUEENTRY
_FEATUREOUTLIERMETA.fields_by_name['cols_strategy'].message_type = _FEATUREOUTLIERMETA_COLSSTRATEGYENTRY
_FEATUREOUTLIERTIONMETA.fields_by_name['imputer_meta'].message_type = _FEATUREOUTLIERMETA
DESCRIPTOR.message_types_by_name['FeatureOutlierMeta'] = _FEATUREOUTLIERMETA
DESCRIPTOR.message_types_by_name['list'] = _LIST
DESCRIPTOR.message_types_by_name['FeatureOutliertionMeta'] = _FEATUREOUTLIERTIONMETA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FeatureOutlierMeta = _reflection.GeneratedProtocolMessageType('FeatureOutlierMeta', (_message.Message,), {

  'MissingValueEntry' : _reflection.GeneratedProtocolMessageType('MissingValueEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEATUREOUTLIERMETA_MISSINGVALUEENTRY,
    '__module__' : 'feature_outliertion_meta_pb2'
    # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.MissingValueEntry)
    })
  ,

  'ColsStrategyEntry' : _reflection.GeneratedProtocolMessageType('ColsStrategyEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEATUREOUTLIERMETA_COLSSTRATEGYENTRY,
    '__module__' : 'feature_outliertion_meta_pb2'
    # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta.ColsStrategyEntry)
    })
  ,
  'DESCRIPTOR' : _FEATUREOUTLIERMETA,
  '__module__' : 'feature_outliertion_meta_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.FeatureOutlierMeta)
  })
_sym_db.RegisterMessage(FeatureOutlierMeta)
_sym_db.RegisterMessage(FeatureOutlierMeta.MissingValueEntry)
_sym_db.RegisterMessage(FeatureOutlierMeta.ColsStrategyEntry)

list = _reflection.GeneratedProtocolMessageType('list', (_message.Message,), {
  'DESCRIPTOR' : _LIST,
  '__module__' : 'feature_outliertion_meta_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.list)
  })
_sym_db.RegisterMessage(list)

FeatureOutliertionMeta = _reflection.GeneratedProtocolMessageType('FeatureOutliertionMeta', (_message.Message,), {
  'DESCRIPTOR' : _FEATUREOUTLIERTIONMETA,
  '__module__' : 'feature_outliertion_meta_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.FeatureOutliertionMeta)
  })
_sym_db.RegisterMessage(FeatureOutliertionMeta)


DESCRIPTOR._options = None
_FEATUREOUTLIERMETA_MISSINGVALUEENTRY._options = None
_FEATUREOUTLIERMETA_COLSSTRATEGYENTRY._options = None
# @@protoc_insertion_point(module_scope)