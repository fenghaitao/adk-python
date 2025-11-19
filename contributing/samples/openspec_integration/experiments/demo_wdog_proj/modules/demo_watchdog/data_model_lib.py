# INTEL CONFIDENTIAL

# © 2024 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cache, wraps, partial, reduce
import itertools
import operator
from struct import pack, calcsize, Struct
from array import array
import types
import typing
from io import BytesIO
from pathlib import Path

__all__ = ('uint8', 'uint16', 'uint32', 'uint64',
           'int8', 'int32', 'int64',
           'Ref', 'List', 'String', 'Member', 'EntitySpec', 'DataModel',
           'Bool', 'Optional')

class Error(Exception): pass

class Datatype(ABC):
    @abstractmethod
    def c_types(self, name) -> list[(str, "CScalar")]: pass

class CScalar(Datatype):
    '''A concrete C type'''
    @property
    @abstractmethod
    def alignment(self): pass
    @property
    @abstractmethod
    def name(self):
        '''Type name in C'''
    @property
    @abstractmethod
    def typecode(self) -> str:
        '''format string for struct.pack'''
    def c_types(self, name) -> list[(str, "CScalar")]:
        return [(name, self)]

@dataclass(frozen=True)
class uint8(CScalar):
    alignment = 1
    name = 'uint8'
    typecode = 'B'

@dataclass(frozen=True)
class int8(CScalar):
    alignment = 1
    name = 'int8'
    typecode = 'b'

@dataclass(frozen=True)
class int32(CScalar):
    alignment = 4
    name = 'int32'
    typecode = 'i'

@dataclass(frozen=True)
class uint16(CScalar):
    alignment = 2
    name = 'uint16'
    typecode = 'H'

@dataclass(frozen=True)
class uint32(CScalar):
    alignment = 4
    name = 'uint32'
    typecode = 'I'

@dataclass(frozen=True)
class uint64(CScalar):
    alignment=8
    name = 'uint64'
    typecode = 'Q'

@dataclass(frozen=True)
class int64(CScalar):
    alignment=8
    name = 'int64'
    typecode = 'q'

# References are represented as uint32 indices in C. When exposed to
# the user in the generated accessor API, they are wrapped in a struct
# for type-safety. The name of this struct depends on DataModel.name.
@dataclass(frozen=True)
class Ref(uint32):
    # EntitySpec.name
    entity_name: str

@dataclass(frozen=True)
class Optional(uint32):
    elem_type: Ref
    def __post_init__(self):
        if not isinstance(self.elem_type, Ref):
            raise Error('optional must be Ref')

@dataclass(frozen=True)
class Bool(Datatype):
    alignment = 1
    name = 'uint8'
    typecode = 'B'
    def c_types(self, name):
        return [(name, uint8())]

# non-CScalar datatypes represent Python types used when constructing
# entity instances in Python.
# TODO: things are currently a bit too hardcoded, e.g., we currently
# don't support list items that are lists or strings.
@dataclass
class List(Datatype):
    elem_type: CScalar
    # can be uint8 for lists of fields in a register
    sz_type: CScalar = uint32()
    def __post_init__(self):
        if (not isinstance(self.elem_type, CScalar)
            or isinstance(self.elem_type, Optional)):
            raise Error('list element type must be integer or Ref')
        if (not isinstance(self.sz_type, CScalar)
            or isinstance(self.sz_type, (Ref, Optional))):
            raise Error('list size type must be integer')
    def c_types(self, name):
        yield (f'{name}_size', self.sz_type)
        yield (f'{name}_first_pool_idx', uint32())

class String(Datatype):
    def __init__(self):
        super().__init__()
    def c_types(self, name):
        return [(f'{name}_pool_idx', uint32())]

@dataclass(eq=False)
class Member:
    '''A member of an entity. Corresponds to one or two struct members.'''
    name: str
    type: Datatype

def flatten(nested_list: list):
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

@dataclass(eq=False)
class FlyweightGroup:
    members: list[str]=field(default_factory=list)
    subgroups: list["FlyweightGroup"]=field(default_factory=list)
    def transitive_members(self):
        yield from self.members
        for g in self.subgroups:
            yield from g.transitive_members()

@dataclass(eq=False)
class EntitySpec(ABC):
    '''Specification of an entity type. An entity is much like a struct type:
    it has a number of *members*; each one has a name and a type.

    The members of an EntitySpec specifies how instances of this entity
    should be input to a DataModel's serializer. It also specifies how
    accessors of these members are named when generating a deserializer.

    `flyweights` specifies what flyweight optimizations are to be applied.
    '''
    name: str
    direct_members: list[Member]
    transitive_members: list[Member]
    direct_flyweights: list["EntitySpec"]
    def __repr__(self):
        return f'EntitySpec({self.name}, {self.direct_members}, {self.direct_flyweights})'
    # used for accessor prefixes, and references in Ref
    def __init__(self,
                 name: str,
                 members: list[Member] = (),
                 # The members for which flyweight optimization is applied,
                 # represented as a FlyweightGroup object. For instance, this expression:
                 # ```
                 # FlyweightGroup(
                 #     members=['a', 'b'],
                 #     subgroups=FlyweightGroup(
                 #         members=['c', 'd']))
                 # ```
                 #
                 # means that members named `c` and `d` are stored
                 # together separately, unifying all equal instances,
                 # and that each entity instance access these through
                 # a reference. Furthermore, members `a` and `b` together
                 # with this reference are stored separately in a
                 # similar manner: all instances with all four members equal
                 # will be merged to one, and the base instance accesses these
                 # through a reference. `None` disable flyweight optimization.
                 flyweighted: typing.Optional[list[FlyweightGroup]]=None,
                 # The set of members for which flyweight optimization
                 # is not applied.  It is an error if not each member
                 # is listed exactly once in `flyweighted` or
                 # `not_flyweighted`; this protects from adding
                 # non-flyweighted members to an entity by mistake.
                 not_flyweighted: typing.Optional[list[str]]=None):
        self.name = name
        self.transitive_members = members
        members_by_name = {
            member.name: member for member in members}
        if len(members_by_name) != len(members):
            raise Error('member name duplicated')
        if flyweighted is None:
            self.direct_flyweights = []
            self.direct_members = members
            if not_flyweighted is not None and set(not_flyweighted) != {
                    m.name for m in members}:
                raise Error('`not_flyweighted` is only useful as a complement'
                            ' to `flyweighted`')
        else:
            if not_flyweighted is None:
                raise Error('not_flyweighted should be provided together with flyweighted')
            for m in not_flyweighted:
                if m not in members_by_name:
                    raise Error(
                        f'No member named {m}, declared as '
                        ' not_flyweighted')
            for g in flyweighted:
                for m in g.transitive_members():
                    if m not in members_by_name:
                        raise Error(
                            f'No member named {m}, declared as '
                            ' flyweighted')
            self.direct_flyweights = [
                EntitySpec(
                    f'{name}_{i}',
                    members=[members_by_name[m] for m in g.transitive_members()],
                    flyweighted=g.subgroups,
                    not_flyweighted=g.members)
                for (i, g) in enumerate(flyweighted)]
            self.direct_members = [m for m in members
                                   if m.name in not_flyweighted]
            for m in members:
                m_flyweighted = {
                    fw for fw in self.transitive_flyweights()
                    if any(fwm.name == m.name for fwm in fw.direct_members)}
                if m_flyweighted and m.name in not_flyweighted:
                    raise Error(f'member {m.name} present in both flyweighted'
                                ' and not_flyweighted')
                if not m_flyweighted and m.name not in not_flyweighted:
                    raise Error(f'member {m.name} present in neither flyweighted'
                                ' nor not_flyweighted')
                if len(m_flyweighted) > 1:
                    raise Error(f'member {m.name} assigned to two different'
                                ' flyweight groups')
            for fw in self.direct_flyweights:
                if not fw.direct_members and not fw.direct_flyweights:
                    raise Error('empty flyweight specification')

    def transitive_flyweights(self):
        yield from self.direct_flyweights
        for fw in self.direct_flyweights:
            yield from fw.transitive_flyweights()

    def direct_struct_members(self):
        '''The struct members corresponding to direct members of this entity,
        i.e., excluding flyweight references'''
        members = []
        for m in self.direct_members:
            if isinstance(m.type, List):
                members.extend([
                    (f'{m.name}_size', m.type.sz_type),
                    (f'{m.name}_first_pool_idx', uint32())])
            elif isinstance(m.type, String):
                members.append((f'{m.name}_pool_idx', uint32()))
            else:
                assert isinstance(m.type, (CScalar, Bool))
                members.append((m.name, m.type))
        return members

    def struct_type(self, name):
        direct_members = self.direct_struct_members()
        direct_int_members = [(n, t) for (n, t) in direct_members
                              if not isinstance(t, Bool)]
        direct_bit_members = [(n, t) for (n, t) in direct_members
                              if isinstance(t, Bool)]
        sorted_int_members = sorted(
            direct_int_members + [(fw.name, uint32())
                                  for fw in self.direct_flyweights],
            key=lambda pair: pair[1].alignment, reverse=True)
        return 'struct {\n%s%s} %s' % (
            ''.join(f'  {t.name} {name};\n'
                    for (name, t) in sorted_int_members),
            f'  uint8 _bits[{(len(direct_bit_members) + 7) // 8}];\n'
            if direct_bit_members else '',
            name)

    def _serialize_info(self):
        direct_members = self.direct_struct_members()
        # Data is supplied to serialization as pairs of tuples,
        # ((entity-member, ..), (flyweight-id, ..)), using the order
        # given in the EntitySpec, where lists are represented by two
        # adjacent integers, and everything else is represented as a
        # single integer. When serializing we want to store the widest
        # members first, to avoid excess alignment padding.
        # bit_member_permutation and int_member_permutation are lists that
        # allow us to quickly reorder the input data.
        sorted_members = sorted(
            [(i, t) for (i, (_, t)) in enumerate(direct_members)]
            + [(len(direct_members) + i, uint32())
               for i in range(len(self.direct_flyweights))],
            key=lambda pair: pair[1].alignment,
            reverse=True)
        bit_member_permutation = [i for (i, t) in sorted_members
                                   if isinstance(t, Bool)]
        int_member_permutation = [i for (i, t) in sorted_members
                                  if not isinstance(t, Bool)]
        fmt = ''.join(t.typecode for (i, t) in sorted_members
                      if not isinstance(t, Bool))
        align = f'0{fmt[0]}' if fmt else ''

        struct = Struct(
            fmt + "B" * ((len(bit_member_permutation) + 7) // 8) + align)
        return (bit_member_permutation,
                int_member_permutation,
                struct)

    def serialized_size(self):
        (_, _, s) = self._serialize_info()
        return s.size

    def serialize_instances(
            # (explicit struct members, flyweight ref members)
            self, instances: list[(tuple[int|bool, ...], tuple[int, ...])]):
        (bit_member_permutation,
         int_member_permutation,
         s) = self._serialize_info()

        pack = s.pack
        chain = itertools.chain
        num_bits = len(bit_member_permutation)
        return [
            pack(*chain(
                (members[i] for i in int_member_permutation),
                (reduce(operator.or_,
                        (members[arg] << i
                         for (i, arg) in enumerate(
                                 bit_member_permutation[low:high])),
                        0)
                 # TODO: want itertools.batched from python 3.12
                 for (low, high) in itertools.pairwise(
                         range(0, num_bits + 8, 8)))))
            for members in (direct + fw for (direct, fw) in instances)]

    # Inverse of serialize_instances
    def deserialize_instances(self, buf, num):
        (bit_member_permutation,
         int_member_permutation,
         s) = self._serialize_info()
        start_points = (range(0, s.size * num, s.size)
                        if s.size else [0] * num)
        for sub_buf in [buf[start:start + s.size]
                        for start in start_points]:
            values_sorted = s.unpack(sub_buf)
            # Apply permutation in reverse
            restored = [None] * (len(int_member_permutation)
                                 + len(bit_member_permutation))
            bit_splitpoint = (
                len(values_sorted) - (len(bit_member_permutation) + 7) // 8)
            int_values = values_sorted[:bit_splitpoint]
            bitfield_values = values_sorted[bit_splitpoint:]
            for (bit, i) in enumerate(bit_member_permutation):
                restored[i] = bool((bitfield_values[bit // 8] >> (bit % 8)) & 1)
            for (i, value) in zip(
                    int_member_permutation, int_values, strict=True):
                restored[i] = value
            split = len(self.direct_struct_members())
            yield (tuple(restored[:split]), tuple(restored[split:]))

class ListPoolSerializer:
    def __init__(self, elem_type: CScalar):
        self.num = 0
        self.elem_type = elem_type
        self.elems: dict[tuple[int], int] = {}
    def index(self, elem: tuple[int]) -> int:
        try:
            return self.elems[elem]
        except KeyError:
            ret = self.elems[elem] = self.num
            self.num += len(elem)
            return ret

class StringSerializer:
    '''Bookkeep a set of strings and how they are serialized'''
    def __init__(self):
        self.str_to_key: dict[str, bytes] = {}
        self.strings: dict[bytes, int] = {}
        self.acc_len = 0
        self.blobs = []
    def add(self, s: str):
        if s in self.str_to_key:
            return
        key = s.encode('utf-8')
        self.str_to_key[s] = key
        if key not in self.strings:
            self.strings[key] = self.acc_len
            self.acc_len += len(key) + 1
    def index(self, s: str):
        try:
            return self.strings[s]
        except KeyError:
            blob = s.encode('utf-8') + b'\0'
            self.blobs.append(blob)
            ret = self.strings[s] = self.acc_len
            self.acc_len += len(blob)
            return ret
        return self.strings[self.str_to_key[s]]
    def dump(self):
        return b''.join(self.blobs)

def pad8(blob: bytes):
    return blob + b'\0' * ((8 - len(blob)) & 7)

base_dialect_impls = {'bank', 'reg', 'field', 'handles'}

class DataModel:
    '''A specification of the DDM data model for a particular DDM dialect.
    A `DataModel` consists of specification of every DDM entity type of the
    dialect, together with the members of that entity kind.

    Example instantiation:
    ```
    dm = DataModel([
        EntitySpec(
            'bank', members=(Member('regs', List(Ref('reg'))),)),
        EntitySpec(
            'reg',
            members=(
                Member('bank', Ref('bank')),
                Member('name', String()),
                Member('offset', uint64()),
                Member('fields', List(Ref('field'), sz_type=uint8())),
                # ...
            )
        ),
        EntitySpec(
            'field',
            members=(
                Member('reg', Ref('reg')),
                Member('lsb', uint8()),
                ...
            ),
        ),
    ])
    ```
'''
    def __init__(self, entities: list[EntitySpec]):
        self.entities = entities
        self.flyweights = flyweights = [
            fw for e in entities for fw in e.transitive_flyweights()]
        entity_names = {spec.name for spec in entities}
        self.entity_specs = {r.name: r for r in entities + flyweights}
        if len(self.entity_specs) != len(entities) + len(flyweights):
            raise Error("each EntitySpec must have a unique name")
        for spec in self.entity_specs.values():
            for p in spec.direct_members:
                t = p.type.elem_type if isinstance(p.type, List) else p.type
                if isinstance(t, Optional):
                    t = t.elem_type
                if (isinstance(t, Ref)
                    and t.entity_name not in entity_names):
                    raise Error(
                        f"Invalid entity reference Ref('{t.entity_name}')"
                        f" in member {spec.name}.{p.name}")
        list_pools = {
            member.type.elem_type.name: member.type.elem_type
            for spec in entities + flyweights
            for member in spec.direct_members
            if isinstance(member.type, List)}
        self.list_pool_types = {k: list_pools[k]
                                for k in sorted(list_pools)}
        # if 'x' is a flyweight and 'y' in
        # entity_specs['x'].flyweights, then 'y' appears before 'x' in
        # this list
        # TODO: remove, redundant
        self.flyweights_topsorted: dict[str, None] = {
            fw.name: None for spec in entities
            for fw in reversed(list(spec.transitive_flyweights()))}
        # TODO: remove, redundant
        self.transitive_flyweights = {
            spec.name: spec.transitive_flyweights
            for spec in entities}

    def flat_members(self, spec: EntitySpec) -> list[(Member, tuple[str])]:
        def rec(spec: EntitySpec) -> list[(Member, tuple[str])]:
            for p in spec.direct_members:
                yield (p, (spec.name,))
            for fw in spec.direct_flyweights:
                for (member, path) in rec(self.entity_specs[fw.name]):
                    yield (member, (spec.name,) + path)
        return dict(rec(spec))

    def _generate_decoder(self, name: str) -> (str, str):
        typedefs = []
        functions = []
        header = ''
        for inc in ['simics/base/types.h', 'simics/util/alloc.h',
                    'simics/util/help-macros.h', 'simics/util/swabber.h']:
            header += f'#include <{inc}>\n'
        for spec in self.entities:
            typedefs.append('struct { uint32 idx; }'
                  f' {name}_{spec.name}_t')
            functions.append(
                (f'{name}_{spec.name}_t\n'
                 f'{name}__mk__{spec.name}(uint32 i)',
                 '{\n'
                 f'  return ({name}_{spec.name}_t){{i}};\n'
                 '}'))
            functions.append(
                ('uint32\n'
                 f'{name}__id__{spec.name}('
                 f'{name}_{spec.name}_t i)',
                 '{\n'
                 f'  return i.idx;\n'
                 '}'))

        sizes_def = 'struct {\n'
        for spec in self.entities + self.flyweights:
            sizes_def += (f'  uint32 {spec.name};\n')
        sizes_def += (f'  uint32 string_pool;\n')
        for typename in self.list_pool_types:
            sizes_def += (f'  uint32 {typename}_pool;\n')
        sizes_def += (f'}} _{name}_sizes_t')
        typedefs.append(sizes_def)

        for spec in self.entities + self.flyweights:
            typedefs.append(spec.struct_type(f'_{name}_{spec.name}_t'))

        decls = itertools.chain(
            [f'_{name}_sizes_t sz'],
            (f'const _{name}_{spec.name}_t *{spec.name}'
             for spec in self.entities + self.flyweights),
            ['const char *string_pool'],
            (f'const {typename} *{typename}_pool'
             for typename in self.list_pool_types))
        typedefs.append(
            'struct {\n' + ''.join(f'  {decl};\n' for decl in decls)
            + f'}} {name}_t')

        for spec in self.entities:
            functions.append((
                f'uint32\n{name}__num__{spec.name}(const {name}_t *_indep)',
                '{\n'
                f'  return _indep->sz.{spec.name};\n'
                '}'))
            for (member, path) in self.flat_members(spec).items():
                # each type in the data model specification can
                # give multiple struct members and thus multiple
                # accessor functions. So we need to make a one-to-many
                # distinction between datatype in the model
                # specification, vs C type.

                # TODO: currently implemented in an extremely ugly
                # fashion with much code duplication
                if isinstance(member.type, Optional):
                    ref_type = member.type.elem_type
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    value = f'_indep->{path[-1]}[{idx}].{member.name}'
                    arglist = (
                        f'(const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name})')
                    functions.append((
                        'bool\n'
                        f'{name}_{spec.name}_{member.name}_valid{arglist}\n',
                        '{\n'
                        f'  return {value} != 0;\n'
                        '}'))
                    rettype = f'{name}_{ref_type.entity_name}_t'
                    functions.append((
                        f'{rettype}\n'
                        f'{name}_{spec.name}_{member.name}{arglist}\n',
                        '{\n'
                        f'  uint32 value = {value};'
                        f'  FATAL_ERROR_IF({value} == 0,'
                        f' "Cannot follow {member.name} member in {spec.name}:'
                        ' null reference");\n'
                        f'  return ({rettype}){{.idx=value - 1}};\n'
                        '}'))
                elif isinstance(member.type, CScalar):
                    rettype = (
                        f'{name}_{member.type.entity_name}_t'
                        if isinstance(member.type, Ref) else member.type.name)
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    ret = f'_indep->{path[-1]}[{idx}].{member.name}'
                    if isinstance(member.type, Ref):
                        ret = (
                            f'({name}_{member.type.entity_name}_t)'
                            f'{{.idx={ret}}}')
                    functions.append((
                        f'{rettype}\n'
                        f'{name}_{spec.name}_{member.name}('
                        f'const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name})\n',
                        '{\n'
                        f'  return {ret};\n'
                        '}'))
                elif isinstance(member.type, Bool):
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    bit_index = [
                        m.name for m in self.entity_specs[path[-1]].direct_members
                        if isinstance(m.type, Bool)].index(member.name)
                    functions.append((
                        f'bool\n'
                        f'{name}_{spec.name}_{member.name}('
                        f'const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name})',
                        '{\n'
                        f'  return (_indep->{path[-1]}[{idx}]._bits'
                        f'[{bit_index // 8}] & {1 << (bit_index & 7)}) != 0;\n'
                        '}'))
                elif isinstance(member.type, String):
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    functions.append((
                        'const char *\n'
                        f'{name}_{spec.name}_{member.name}('
                        f'const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name})',
                        '{\n'
                        '  return &_indep->string_pool['
                        f'_indep->{path[-1]}[{idx}].{member.name}_pool_idx];\n'
                        '}'))
                else:
                    assert isinstance(member.type, List)
                    elem_type = member.type.elem_type
                    # Validated in __init__
                    # TODO: we could also permit Bool and String
                    assert isinstance(elem_type, CScalar)
                    rettype = (
                        f'{name}_{elem_type.entity_name}_t'
                        if isinstance(elem_type, Ref) else elem_type.name)
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    functions.append((
                        f'{member.type.sz_type.name}\n'
                        f'{name}_{spec.name}_{member.name}_len('
                        f'const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name})',
                        '{\n'
                        f'  return _indep->{path[-1]}[{idx}]'
                        f'.{member.name}_size;\n'
                        '}'))
                    idx = f'{spec.name}.idx'
                    for (parent, child) in zip(path, path[1:]):
                        idx = f'_indep->{parent}[{idx}].{child}'
                    ret = (
                        f'_indep->{elem_type.name}_pool['
                        f'_indep->{path[-1]}[{idx}]'
                        f'.{member.name}_first_pool_idx + index]')
                    if isinstance(elem_type, Ref):
                        ret = (f'{name}__mk__{elem_type.entity_name}('
                               f'{ret})')
                    functions.append((
                        f'{rettype}\n'
                        f'{name}_{spec.name}_{member.name}_item('
                        f'const {name}_t *_indep,'
                        f' {name}_{spec.name}_t {spec.name},'
                        f' {member.type.sz_type.name} index)',
                        '{\n'
                        '  FATAL_ERROR_IF(index >='
                        f'_indep->{path[-1]}[{idx}].{member.name}_size,'
                        ' "index %u out-of-bounds in list of size %u",'
                        ' index,'
                        f' _indep->{path[-1]}[{idx}].{member.name}_size);\n'
                        f'  return {ret};\n'
                        '}'))

        align_pos = 'pos = (pos + 7) & ~7;'
        new_body = (
            '{\n'
            f'  {name}_t *ret'
                f' = MM_MALLOC(1, {name}_t);\n'
            '  const uint8 *mapped = data.data;\n'
            '  uint64 size = data.len;\n'
            '  ASSERT(size >= 8);\n'
            '  uint64 hash = UNALIGNED_LOAD_LE64(mapped);\n'
            '  FATAL_ERROR_IF(hash != expected_hash, '
            '"Glue and generated binary out-of-sync");\n'
            f'  int64 pos = 8;\n'
            f'  ASSERT(sizeof(_{name}_sizes_t) <= size);\n'
            f'  memcpy(&ret->sz, mapped + pos, sizeof(_{name}_sizes_t));\n'
            f'  pos += sizeof(_{name}_sizes_t);\n'
            f'  {align_pos}\n')

        for spec in self.entities + self.flyweights:
            new_body += (
                f'  ret->{spec.name}'
                f' = (const _{name}_{spec.name}_t *)(mapped + pos);\n'
                f'  pos += sizeof(*ret->{spec.name})'
                f' * ret->sz.{spec.name};\n'
                f'  {align_pos}\n')
        new_body += (
            '  ret->string_pool = (const char *)(mapped + pos);\n'
            f'  pos += sizeof(char) * ret->sz.string_pool;\n'
            f'  {align_pos}\n')
        for typename in self.list_pool_types:
            new_body += (
                f'  ret->{typename}_pool = (const {typename} *)'
                '(mapped + pos);\n'
                f'  pos += sizeof({typename}) * ret->sz.{typename}_pool;\n'
                f'  {align_pos}\n')
        new_body += (
            '  FATAL_ERROR_IF(pos != size,\n'
            '      "unexpected datablob size: expected %lld, got %lld",\n'
            '      pos, size);\n')
        new_body += (
            '  return ret;\n'
            '}')

        functions.append((
            f'{name}_t *\n'
            f'__new_{name}(bytes_t data, uint64 expected_hash)', new_body))

        dml = ''
        for typedef in typedefs:
            header += f'typedef {typedef};\n'
            dml += f'extern typedef {typedef};\n'
        for (signature, body) in functions:
            header += f'static inline {signature}\n{body}\n\n'
            dml += f'extern {signature};\n'
        return (header, dml)

    def generate_dmlfile(self, path: Path|str, name: str,
                       obj_name: str|None=None):
        '''\
Generates a DML file that provides the basic abstractions needed to access the
data of a loaded DDM
binary. This includes:
* The type <tt><em>dia</em>_t</tt> representing a loaded DDM of the
  dialect.
* For every entity kind <em>kind</em>, the type of the references to
  that kind <tt><em>dia</em>_<em>kind</em>_t</tt>.
* Accessor methods of the dialect group that given a reference to an
  entity of a particular kind, allows you to access any property of
  that entity, if that property is a member of the entity kind.
  The signature of each accessor method depends on the member type.
* Establishes a number of hooks and low-level implementation code on top of
  which the dialect implementation should be built.
'''
        if obj_name is None:
            obj_name = name
        with open(path, 'wt') as f:
            self._generate_dmlfile(f, name, obj_name)

    def _generate_dmlfile(self, f: typing.TextIO, name: str,
                          obj_name: str):
        f.write('dml 1.4;\n\n')

        (header, dml) = self._generate_decoder(name)
        f.write('header %{\n')
        f.write(header)
        f.write('%}\n\n')
        f.write(dml)

        f.write('\n')
        f.write(f'group {obj_name} is ddm_dialect_base {{\n')
        f.write(f'  param spec_type_carrier = *cast(NULL, {name}_t *);\n')
        f.write(f'  param _new_spec = __new_{name};\n')
        f.write(f'  param assoc_vtable_type_carrier = *cast(NULL, {name}_assoc_vtable *);\n')
        f.write(f'  param each_dia_bank_expr = each {name}_assoc_to_bank in (dev);\n')
        for spec in self.entities:
            f.write(
                f'  param {spec.name}_type_carrier = *cast(NULL, {name}_{spec.name}_t *);\n')
            if spec.name == 'bank':
                f.write(f'  param bank_template_carrier = *cast(NULL, {name}_assoc_to_bank *);\n')
            f.write(
                f'  group {spec.name} is {name}_dialect_base_{spec.name};\n')
        f.write('}\n')
        handles = ([{member.name: member for member in self.flat_members(spec)}
                    for spec in self.entities if spec.name == 'handles']
                   or [[]])[0]
        for spec in self.entities:
            f.write(f'template {name}_dialect_base_{spec.name} ')
            if spec.name in base_dialect_impls:
                f.write(f'is ddm_dialect_base_{spec.name} ')
            f.write('{\n')
            f.write(f'  param __count = {name}__num__{spec.name};\n')
            f.write(f'  param __id   = {name}__id__{spec.name};\n')
            f.write(f'  param __mk   = {name}__mk__{spec.name};\n')
            for member in self.flat_members(spec):
                if isinstance(member.type, List):
                    elem_type = member.type.elem_type
                    assert isinstance(elem_type, CScalar)
                    f.write(f'  param _{member.name}_item = {name}_{spec.name}_{member.name}_item;\n')
                    f.write(f'  param _{member.name}_len = {name}_{spec.name}_{member.name}_len;\n')
                    rettype = (
                        f'{name}_{elem_type.entity_name}_t'
                        if isinstance(elem_type, Ref) else elem_type.name)
                    f.write(f'  independent method {member.name}_len({name}_{spec.name}_t _{spec.name}) -> (uint32) default {{\n')
                    f.write(f'    return this._{member.name}_len(dia.spec(), _{spec.name});\n')
                    f.write('  }\n')
                    f.write(f'  independent method {member.name}_item({name}_{spec.name}_t _{spec.name}, uint32 _i) -> ({rettype}) default {{\n')
                    f.write(f'    return this._{member.name}_item(dia.spec(), _{spec.name}, _i);\n')
                    f.write('  }\n')
                elif isinstance(member.type, Optional):
                    ref_type = member.type.elem_type
                    assert isinstance(ref_type, Ref)
                    f.write(f'  param _{member.name}_valid = {name}_{spec.name}_{member.name}_valid;\n')
                    f.write(f'  param _{member.name} = {name}_{spec.name}_{member.name};\n')
                    rettype = (
                        f'{name}_{ref_type.entity_name}_t'
                        if isinstance(elem_type, Ref) else elem_type.name)
                    f.write(f'  independent method {member.name}_valid({name}_{spec.name}_t _{spec.name}) -> (bool) default {{\n')
                    f.write(f'    return this._{member.name}_valid(dia.spec(), _{spec.name});\n')
                    f.write('  }\n')
                    f.write(f'  independent method {member.name}({name}_{spec.name}_t _{spec.name}) -> ({rettype}) default {{\n')
                    f.write(f'    return this._{member.name}(dia.spec(), _{spec.name});\n')
                    f.write('  }\n')
                else:
                    member_name = member.name
                    if member_name in {'name', 'desc'}:
                        member_name = member_name + '_'
                    f.write(f'  param _{member_name} = {name}_{spec.name}_{member.name};\n')
                    if isinstance(member.type, CScalar):
                        rettype = (
                            f'{name}_{member.type.entity_name}_t'
                            if isinstance(member.type, Ref)
                            else member.type.name)
                    elif isinstance(member.type, Bool):
                        rettype = 'bool'
                    else:
                        assert isinstance(member.type, String)
                        rettype = 'const char *'
                    f.write(f'  independent method {member_name}({name}_{spec.name}_t _{spec.name}) -> ({rettype}) default {{\n')
                    f.write(f'    return this._{member_name}(dia.spec(), _{spec.name});\n')
                    f.write('  }\n')
            if spec.name in handles:
                f.write(f'''
  independent startup memoized method _assoc_ht() -> (ht_int_table_t) {{
    local ht_int_table_t ret;
    ht_init_int_table(&ret);
    foreach assoc in (each {name}_assoc_to_{spec.name} in (dev)) {{
        local {name}_assoc_to_{spec.name} *entry = new {name}_assoc_to_{spec.name};
        *entry = assoc;
        ht_insert_int(&ret, this.__id(entry->ddm_{spec.name}()), entry);
    }}
    return ret;
  }}

  independent method get_assoc({name}_{spec.name}_t item) -> ({name}_assoc_to_{spec.name}) throws {{
    local ht_int_table_t ht = _assoc_ht();
    local {name}_assoc_to_{spec.name} *assoc = ht_lookup_int(&ht, this.__id(item));
    if (assoc == NULL) throw;
    return *assoc;
  }}''')
            elif spec.name in {'reg', 'field', 'bank'}:
                f.write(f'''
  independent method get_assoc({name}_{spec.name}_t item) -> ({name}_assoc_to_{spec.name}) throws {{
    throw
  }}''')
            f.write('\n}\n')

        f.write('\n')
        f.write(f'''
template _{name}_assoc_vtable_downcast_impl is {name}_assoc_vtable {{
  shared independent method _ddm_assoc_vtable_downcast() -> (_traitref_t) {{
    local {name}_assoc_vtable ref = cast(this, {name}_assoc_vtable);
    return *cast(&ref, _traitref_t *);
  }}
}}

in each {name}_assoc_vtable {{ is _{name}_assoc_vtable_downcast_impl; }}

''')
        for spec in {'bank', 'reg', 'field'}.union(handles):
            f.write(f'template {name}_assoc_to_{spec}_base ')
            if spec in {'bank', 'reg', 'field'}:
                f.write(f'is ddm_assoc_to_{spec} {{\n')
            else:
                f.write('{\n')
                f.write(f'  param first_{spec}_index : uint32;\n')
            f.write(f'''
  param dia = dev.{name};
  shared independent method ddm_{spec}() -> ({name}_{spec}_t) {{\n'''[1:])
            if spec in handles:
                f.write(f'''
    local {name}_assoc_to_{spec}_base assoc = this;
    return {name}.handles._{spec}_item(dev.{name}.spec(),
        {name}.handles.__mk(0),
        assoc.first_{spec}_index
        + cast(&assoc, _traitref_t *)->id.encoded_index);
  }}\n'''[1:])
            else:
                f.write(f'''
    assert false;
  }}
  error "Data model does not permit by-name associations to {spec}";\n'''[1:])
            if spec == 'bank':
                f.write(f'''
  in each ddm_assoc_vtable {{ is _{name}_assoc_vtable_downcast_impl; }}

  shared method little_endian_byte_order({name}_reg_t reg) -> (bool);

  shared method validate_reg_write_impl({name}_reg_t reg,
                                        uint64 curr_val, uint64 written_val,
                                        uint64 enabled_bits, void *aux)
                                    -> (uint64);
  shared method validate_reg_read_impl({name}_reg_t reg, uint64 curr_val,
                                       uint64 enabled_bits, void *aux)
                                   -> (uint64);

  shared method reg_write_impl({name}_reg_t reg, uint64 curr_val,
                               uint64 written_val, uint64 enabled_bits,
                               void *aux) -> (uint64);

  shared method reg_read_impl({name}_reg_t reg, uint64 curr_val,
                              uint64 enabled_bits, void *aux) -> (uint64);
'''[1:])
            f.write('}\n')
            f.write(f'in each {name}_assoc_to_{spec} {{ is {name}_assoc_to_{spec}_base; }}\n')


    def collapse_flyweights(self, fw_instances):
        # for each flyweight, all its instances serialized
        flyweight_blobs: dict[str, list[bytes]] = {}
        # For all entity, and for each of its transitive flyweights,
        # the flyweight ID of each spec instance.
        # Leaf flyweights are filled in first.
        spec_flyweight_ids: dict[str, dict[str, array]] = {
            spec.name: {} for spec in self.entities
        }
        for fwname in self.flyweights_topsorted:
            fw = self.entity_specs[fwname]
            # keys are entity instances to be serialized, on the form
            # ((explicit struct members, bool members), flyweight ref members),
            # in serialization order; values are flyweight indices
            fw_member_table: dict[
                (tuple[int, ...], tuple[int, ...]),
                int] = {}
            # one flyweight may be used by multiple entities; find
            # instances of all
            for spec in self.entities:
                if fwname not in fw_instances[spec.name]:
                    continue
                fw_ids = []
                sub_fw_members = (
                    zip(*(spec_flyweight_ids[spec.name][sub_fw.name]
                          for sub_fw in fw.direct_flyweights))
                    if fw.direct_flyweights else itertools.repeat(()))
                for instance in zip(fw_instances[spec.name][fwname],
                                    sub_fw_members):
                    idx = fw_member_table.get(instance)
                    if idx is None:
                        idx = len(fw_member_table)
                        fw_member_table[instance] = idx
                    fw_ids.append(idx)
                spec_flyweight_ids[spec.name][fwname] = fw_ids

            flyweight_blobs[fwname] = fw.serialize_instances(fw_member_table)
        return (flyweight_blobs, spec_flyweight_ids)


    def expand_pools(
            self,
            # For each EntitySpec name, a list of all instances.
            instances_by_spec: dict[str, dict[str, dict[str, object]]]) -> (
                # Returns a quadruple. The first element is a dict,
                # mapping entity name to an iterator of int tuples
                # representing "struct instances"; each struct instance
                # represents the struct members generated from *direct* members
                # of that entity, excluding flyweight references.
                # The tuple has one integer (possibly bool) for each
                # direct struct member.
                # The second element of the return value is a nested dict,
                # which for each entity name, and each of that entity's flyweight,
                # contains an iterator of struct instances, one for each
                # instance of that entity, with the direct members of that
                # flyweight.
                # The third and fourth elements of the return value
                # are functions returning the string pool and array pools,
                # respectively. These are lazy, and only valid after all
                # iterators in the first two elements are exhausted.
                dict[str, Iterable[tuple[int, ...]]],
                dict[str, dict[str, Iterable[tuple[int, ...]]]],
                typing.Callable[(), bytes], typing.Callable[(), list[array]]):
        # For each EntitySpec name, map anchor name to index.
        anchors = {
            specname: {
                anchor: i
                for (i, (anchor, obj)) in enumerate(objs.items())
                if anchor is not None}
            for (specname, objs) in instances_by_spec.items()}

        list_pool_serializers = {
            name: ListPoolSerializer(t)
            for (name, t) in self.list_pool_types.items()}
        string_serializer = StringSerializer()

        def direct_struct_member_tuples(spec, instances):
            '''Return an iterator producing one tuple for each
            instance of the entity, where the tuple has one element
            for each direct struct members of the entity.'''
            # Create one fast iterable for each direct struct member,
            # and use zip to combine these. This avoids if:s in the
            # innermost loops
            def instances_for_member(m):
                if isinstance(m.type, List):
                    elem_type = m.type.elem_type
                    if isinstance(elem_type, Ref):
                        entity_anchors = anchors[elem_type.entity_name]
                        values = []
                        for (anchor, instance) in instances.items():
                            refs = instance[m.name]
                            try:
                                values.append(tuple(
                                    entity_anchors[ref] for ref in refs))
                            # TODO: add similar reporting on other error paths
                            # and add tests
                            except KeyError as e:
                                raise Error(
                                    f"In {spec.name} '{anchor}',"
                                    + f" member '{m.name}':"
                                    + f" no {elem_type.entity_name}"
                                    + f" named {e}")
                    elif isinstance(elem_type, String):
                        # TODO: we can support list of strings
                        assert False
                    elif isinstance(elem_type, Bool):
                        # TODO: we can support list of bools
                        assert False
                    else:
                        values = [tuple(instance[m.name])
                                  for instance in instances.values()]

                    list_id = list_pool_serializers[elem_type.name].index
                    yield (len(v) for v in values)
                    yield (list_id(v) for v in values)
                elif isinstance(m.type, String):
                    yield (string_serializer.index(instance[m.name])
                           for instance in instances.values())
                elif isinstance(m.type, Bool):
                    yield (instance[m.name]
                           for instance in instances.values())
                elif isinstance(m.type, Optional):
                    ref_type = m.type.elem_type
                    assert isinstance(ref_type, Ref)
                    ref_anchors = anchors[ref_type.entity_name]
                    def values():
                        name = m.name
                        for instance in instances.values():
                            ref = instance[name]
                            yield 0 if ref is None else ref_anchors[ref] + 1
                    yield values()
                else:
                    assert isinstance(m.type, CScalar)
                    if isinstance(m.type, Ref):
                        ref_anchors = anchors[m.type.entity_name]
                        values = (
                            ref_anchors[instance[m.name]]
                            for instance in instances.values())
                    else:
                        values = (instance[m.name]
                                  for instance in instances.values())
                    yield values
            instances_by_member = [instances for m in spec.direct_members
                                   for instances in instances_for_member(m)]
            assert len(instances_by_member) == len(spec.direct_struct_members())
            return (zip(*instances_by_member) if instances_by_member
                    else itertools.repeat((), len(instances)))
        entity_instances = {
            spec.name: direct_struct_member_tuples(
                spec, instances_by_spec[spec.name])
            for spec in self.entities}
        fw_instances = {spec.name:
                        {fwspec.name: direct_struct_member_tuples(
                            fwspec, instances_by_spec[spec.name])
                         for fwspec in spec.transitive_flyweights()}
                        for spec in self.entities}
        return (entity_instances,
                fw_instances,
                string_serializer.dump,
                lambda: [
                    array(ser.elem_type.typecode, itertools.chain.from_iterable(
                        ser.elems))
                    for ser in list_pool_serializers.values()])

    def serialize(self, hash_to_write,
                  **objlists: dict[str, dict[str, dict[str, object]]]):
        spec_names = set(spec.name for spec in self.entities)
        errors = set(objlists) - spec_names
        if errors:
            raise Error(f'unknown object types: {errors}')
        errors = spec_names - set(objlists)
        if errors:
            raise Error(f'no object lists for types: {errors}')

        (entity_instances, fw_instances, stringblob,
         list_pools) = self.expand_pools(objlists)

        (flyweight_blobs, spec_flyweight_ids) = self.collapse_flyweights(
            fw_instances)

        entity_blobs = [
            spec.serialize_instances(
                zip(entity_instances[spec.name],
                    zip(*(spec_flyweight_ids[spec.name][fw.name]
                          for fw in spec.direct_flyweights))
                    if spec.direct_flyweights
                    else itertools.repeat(((), ()))))
            for spec in self.entities]

        stringblob = stringblob()
        list_pools = list_pools()
        with BytesIO() as f:
            # hash
            f.write(hash_to_write.to_bytes(8, byteorder='little', signed=True))
            # members of the .sz struct
            sizes = (
                [len(blobs) for blobs in entity_blobs]
                # if arrays is empty, then there are no instances
                # of the flyweighted entity
                + [len(flyweight_blobs[fw.name])
                   for fw in self.flyweights]
                + [len(stringblob)]
                + [len(pool) for pool in list_pools])
            f.write(pack(f'{len(sizes)}{uint32().typecode}0Q', *sizes))
            for blobs in entity_blobs:
                f.write(pad8(b''.join(blobs)))
            for fw in self.flyweights:
                f.write(pad8(b''.join(flyweight_blobs[fw.name])))
            f.write(pad8(stringblob))
            for pool in list_pools:
                f.write(pad8(pool.tobytes()))
            return f.getvalue()

    def deserialize(self, blob_bytes):
        with BytesIO(blob_bytes) as f:
            def read_bytes(sz):
                data = f.read((sz + 7) & ~7)
                assert len(data) >= sz
                return data[:sz]
            def read_array(fmt, n):
                sz = calcsize(fmt) * n
                data = read_bytes(sz)
                return array(fmt, data)
            # skip hash
            _ = read_bytes(8)
            lengths = [len(self.entities), len(self.flyweights), 1,
                       len(self.list_pool_types)]
            nsizes = sum(lengths)
            sizes = read_array(uint32().typecode, nsizes)
            [num_entities, num_flyweights, [stringblob_size], num_listpools] = [
                sizes[start:stop] for (start, stop) in itertools.pairwise(
                    [0] + list(itertools.accumulate(lengths)))]
            entity_data = {
                spec.name: spec.deserialize_instances(read_bytes(
                    spec.serialized_size() * num_instances), num_instances)
                for (spec, num_instances) in zip(self.entities, num_entities)}
            fw_data = {
                spec.name: spec.deserialize_instances(read_bytes(
                    spec.serialized_size() * num_instances), num_instances)
                for (spec, num_instances) in zip(self.flyweights, num_flyweights)}
            stringblob = read_bytes(stringblob_size)
            list_pools = {name: read_array(listtype.typecode, sz)
                          for (sz, (name, listtype)) in zip(
                                  num_listpools, self.list_pool_types.items())}
            rest = f.read()
            assert rest == b'', rest
        def deserialize_one(member_type, elems):
            if isinstance(member_type, Ref):
                return f'{member_type.entity_name}{next(elems)}'
            elif isinstance(member_type, Optional):
                elem = next(elems)
                return (None if elem == 0
                        else f'{member_type.elem_type.entity_name}{elem - 1}')
            elif isinstance(member_type, CScalar):
                return next(elems)
            elif isinstance(member_type, Bool):
                return bool(next(elems))
            elif isinstance(member_type, String):
                elem = next(elems)
                end = stringblob.index(b'\x00', elem)
                return stringblob[elem:end].decode('utf-8')
            elif isinstance(member_type, List):
                size = next(elems)
                first_idx = next(elems)
                els = iter(list_pools[member_type.elem_type.name][
                    first_idx:first_idx + size])
                return [
                    deserialize_one(member_type.elem_type, els)
                    for _ in range(size)]
            else:
                assert False, member_type

        flyweight_instances = {}
        for fwname in self.flyweights_topsorted:
            spec = self.entity_specs[fwname]
            instances = []
            for (direct_struct_members, fw_ids) in fw_data[fwname]:
                instance = {}
                els = iter(direct_struct_members)
                for member in spec.direct_members:
                    instance[member.name] = deserialize_one(member.type, els)
                for (sub_spec, fw) in zip(spec.direct_flyweights, fw_ids, strict=True):
                    instance.update(flyweight_instances[sub_spec.name][fw])
                instances.append(instance)
            flyweight_instances[fwname] = instances
        ret = {}
        for spec in self.entities:
            instances = {}
            for (i, (direct_struct_members, fw_ids)) in enumerate(
                    entity_data[spec.name]):
                instance = {}
                els = iter(direct_struct_members)
                for member in spec.direct_members:
                    instance[member.name] = deserialize_one(member.type, els)
                for (sub_spec, fw) in zip(spec.direct_flyweights, fw_ids, strict=True):
                    instance.update(flyweight_instances[sub_spec.name][fw])
                instances[f'{spec.name}{i}'] = instance
            ret[spec.name] = instances
        return ret
