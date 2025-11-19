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

import os
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from array import array
from data_model_lib import (
    uint8, uint16, uint32, uint64, Ref, String, List, Bool, Optional,
    DataModel, EntitySpec, Member, Error, FlyweightGroup)
import pytest
import traceback

class DataModelFixture(ABC):
    instances = []
    def __init__(self):
        self.test_cases = []
    @staticmethod
    def instance(f):
        ModelFixture.instances.append(f)

    @abstractmethod
    def data_model(self):
        pass

@dataclass
class TestBench:
    tmpdir: Path
    name: str
    model: DataModel
    __test__ = False

    def datafile(self, filename='datafile', fake_hash=0xdeadbeef, **kwargs):
        data = self.model.serialize(hash_to_write=fake_hash, **{
            spec: {obj.get('anchor', f'{i}'):
                   {prop: val for (prop, val) in obj.items()
                    if prop != 'anchor'}
                   for (i, obj) in enumerate(objs)}
            for (spec, objs) in kwargs.items()})
        restored = self.model.deserialize(data)
        assert self.model.serialize(hash_to_write=fake_hash, **restored) == data
        path = Path(self.tmpdir) / filename
        path.write_bytes(data)
        return path

    def run_c(self, body: str, datafile='datafile', pre: str = '',
              linemarks=True):
        frame = traceback.extract_stack()[-2]
        (h, _) = self.model._generate_decoder(self.name)
        (self.tmpdir / 'model.h').write_text(h, 'utf-8')
        tests_c = Path(self.tmpdir) / 'tests.c'
        tests_bin = self.tmpdir / 'tests'
        simics_base = Path(os.environ['SIMICS_BASE'])
        first_lines = (
            '''
#include <setjmp.h>
#include <simics/util/encoding.h>
#include <simics/util/init.h>
#include "model.h"
static jmp_buf on_fatal_error;
static int expected_fatal_errors;
''' + pre +
            f'\nvoid tests(const {self.name}_t *{self.name})'
            '{\n')
        if linemarks:
            # hack: assume body was passed to this function as ''' literal
            # and adjust line info accordingly
            first_lines += (
                f'#line {frame.lineno + 1} "{Path(frame.filename).resolve()}"')
        first_lines += f'{body}\n}}\n'
        if linemarks:
            first_lines += '#line %d "%s"\n' % (
                first_lines.count("\n") + 2, tests_c)
        data = Path(self.tmpdir / datafile).read_bytes()
        data_literal = ''.join('\\x%02x' % b for b in data)
        tests_c.write_text(first_lines + '''
static void
my_assert_error(int line,
             const char *file,
             const char *mod_date,
             const char *message)
{
        fprintf(stderr, "%s:%d: failed assertion: %s\\n", file, line, message);
        exit(1);
}
void my_fatal_error(const char *msg)
{
        if (expected_fatal_errors) {
                expected_fatal_errors -= 1;
                longjmp(on_fatal_error, 1);
        } else {
                fprintf(stderr, "%s", msg);
                exit(1);
        }
}
''' f'''
static const uint8 data[{len(data)}] = "{data_literal}";
int
main(int argc, const char **argv)
{{
        ASSERT(argc == 1);
        initialize_encoding();
        vtutils_set_assert_error_handler(my_assert_error);
        vtutils_set_fatal_error_handler(my_fatal_error);
        {self.name}_t *m = __new_{self.name}(
            (bytes_t){{data, {len(data)}}}, 0xdeadbeef);
        tests(m);
        return 0;
}}
''')
        subprocess.run(
            ['gcc', f'-L{simics_base / "linux64" / "bin"}',
             f'-Wl,-rpath,{simics_base / "linux64" / "bin"}', tests_c,
             '-lvtutils', '-o', tests_bin, '-O2', '-Wall', '-Werror',
             f'-I{simics_base / "src" / "include"}'],
            check=True)
        subprocess.run([tests_bin], check=True)

def test_types():
    assert Ref('foo').name == uint32().name == Optional(Ref('foo')).name
    with pytest.raises(Error):
        List(List(uint32()))
    with pytest.raises(Error):
        List(uint32(), sz_type=Ref('x'))
    with pytest.raises(Error):
        List(uint32(), sz_type=Optional(Ref('x')))
    with pytest.raises(Error):
        List(Optional(Ref('x')))
    # TODO: these could be implemented
    with pytest.raises(Error):
        List(String())
    with pytest.raises(Error):
        List(Bool())
    with pytest.raises(Error):
        List(uint32(), sz_type=Bool())

def test_serialize_instances():
    def expect_serialize(spec, deserialized, serialized):
        assert spec.serialize_instances(deserialized) == serialized
        assert (list(spec.deserialize_instances(b''.join(serialized),
                                               len(deserialized)))
                == deserialized)
    expect_serialize(EntitySpec('_', members=[]),
                     [((), ())] * 10,
                     [b''] * 10)
    expect_serialize(EntitySpec('_', members=[Member('p', uint8())]),
                     [((3,), ())],
                     [b'\x03'])
    expect_serialize(EntitySpec('_', members=[Member('p', Bool())]),
                     [((True,), ())],
                     [b'\x01'])

    a = EntitySpec('a', members=[Member('p', uint8()),
                                 Member('q', uint64()),
                                 Member('r', Bool()),
                                 Member('s', Bool()),
                                 Member('x', uint8()),
                                 Member('y', uint8())],
                   flyweighted=[
                       FlyweightGroup(members=['x']),
                       FlyweightGroup(members=['y'])],
                   not_flyweighted=['p', 'q', 'r', 's'])
    # Members appear in decreasing size order to minimize padding,
    # sometimes interleaving flyweights with other members.
    # Padding is controlled by the largest member.
    expect_serialize(
        a, [((4, 5, True, True), (6, 7))] * 2,
        [b'\x05\0\0\0\0\0\0\0\x06\0\0\0\x07\0\0\0\x04\x03\0\0\0\0\0\0'] * 2)

    # Multiple bool members are packed together
    for (nbools, exp) in [(8, b'\xff'), (9, b'\xff\x01')]:
        expect_serialize(
            EntitySpec(
                'foo', members=[
                    Member(f'p{i}', Bool()) for i in range(nbools)]),
            [((True,) * nbools, ())],
            [exp])


def test_collapse_flyweights():
    # flyweight is collapsed if all members match
    model = DataModel(
        [EntitySpec('x', members=[Member('p', uint8()),
                                  Member('q', Bool())],
                    flyweighted=[FlyweightGroup(members=['p', 'q'])],
                    not_flyweighted=[])])
    assert (
        model.collapse_flyweights(
            {'x': {'x_0': [(1, True), (1, False), (2, True),
                         (1, False)]}})
        == ({'x_0': [b'\x01\x01', b'\x01\x00', b'\x02\x01']},
            {'x': {'x_0': [0, 1, 2, 1]}}))

    # `a` has a nested flyweight, and is only collapsed if both the
    # local members and the sub-flyweight match
    model = DataModel(
        entities=[
            EntitySpec('x', members=[Member('p', uint8()), Member('q', uint8())],
                       flyweighted=[
                           FlyweightGroup(members=['p'],
                                          subgroups=[FlyweightGroup(['q'])])],
                       not_flyweighted=[])])
    assert (
        model.collapse_flyweights(
            {'x': {'x_0': [(3,), (3,), (4,), (3,)],
                   'x_0_0': [(5,), (6,), (5,), (5,)]}})
        == ({'x_0_0': [b'\x05', b'\x06'],
             'x_0': [b'\x00\0\0\0\x03\0\0\0',
                   b'\x01\0\0\0\x03\0\0\0',
                   b'\x00\0\0\0\x04\0\0\0']},
            {'x': {'x_0': [0, 1, 2, 0], 'x_0_0': [0, 1, 0, 0]}}))

def test_expand_pools():
    def expect_result(got, expected):
        (got_pub, got_fw, got_strings, got_lists) = got
        assert ({name: list(instances) for (name, instances) in got_pub.items()},
                {name: {fw: list(instances) for (fw, instances) in fws.items()}
                 for (name, fws) in got_fw.items()},
                got_strings(), got_lists()) == expected
    expect_result(DataModel([]).expand_pools({}),
                  ({}, {}, b'', []))
    model = DataModel(
        [EntitySpec('x', members=[])])
    expect_result(model.expand_pools({'x': {}}),
                  ({'x': []}, {'x': {}}, b'', []))
    expect_result(model.expand_pools({'x': {'a0': {}}}),
                  ({'x': [()]}, {'x': {}}, b'', []))
    model = DataModel(
        [EntitySpec('x', members=[Member('p', uint8())])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': 3}, 'a1': {'p': 4}}}),
        ({'x': [(3,), (4,)]},
         {'x': {}},
         b'', []))

    model = DataModel(
        [EntitySpec('x', members=[Member('p', Bool())])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': True}, 'a1': {'p': False}}}),
        ({'x': [(True,), (False,)]},
         {'x': {}},
         b'', []))

    # An entity with multiple members works
    model = DataModel(
        [EntitySpec('x', members=[
            Member('a', uint8()),
            Member('b', uint8())])])
    expect_result(
        model.expand_pools({'x': {'a0': {'a': 1, 'b': 2}}}),
        ({'x': [(1, 2)]},
         {'x': {}}, b'', []))

    # Flyweight members are included in the second dict
    model = DataModel(
        [EntitySpec('x', members=[Member('p', Bool()),
                                  Member('q', uint8())],
                    flyweighted=[FlyweightGroup(
                        members=['p'],
                        subgroups=[FlyweightGroup(members=['q'])])],
                    not_flyweighted=[])])
    expect_result(
        model.expand_pools({'x': {'x_0': {'p': True, 'q': 3},
                                  'x_0_0': {'p': False, 'q': 4}}}),
        ({'x': [(), ()]},
         {'x': {'x_0': [(True,), (False,)],
                'x_0_0': [(3,), (4,)]},},
         b'', []))
    model = DataModel(
        [EntitySpec('x', members=[Member('p', Ref('x'))])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': 'a1'}, 'a1': {'p': 'a0'}}}),
        ({'x': [(1,), (0,)]},
         {'x': {}},
         b'', []))
    model = DataModel(
        [EntitySpec('x', members=[Member('p', Optional(Ref('x')))])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': 'a1'}, 'a1': {'p': None}}}),
        ({'x': [(2,), (0,)]},
         {'x': {}},
         b'', []))
    model = DataModel(
        [EntitySpec('x', members=[
            Member('p', String())])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': 'xyz'},
                                  'a1': {'p': 'yz'},
                                  'a2': {'p': 'yz'}}}),
        # each string replaced with an index into stringblob
        ({'x': [(0,), (4,), (4,)]},
         {'x': {}},
         b'xyz\0yz\0', []))
    model = DataModel(
        [EntitySpec('x', members=[
            Member('p', List(uint16(), sz_type=uint8()))])])
    expect_result(
        model.expand_pools({'x': {'a0': {'p': [2, 3, 4]},
                                  'a1': {'p': [2, 3]},
                                  'a2': {'p': [2, 3]}}}),
        # one (size, first_index) pair for each element
        ({'x': [(3, 0), (2, 3), (2, 3)]},
         {'x': {}},
         b'', [array('H', [2, 3, 4, 2, 3])]))

def test_refs():
    with pytest.raises(Error):
        # broken Ref type
        DataModel([EntitySpec(
            'a', members=[Member('p', Ref('b'))])])
    with pytest.raises(Error):
        # broken Ref type
        DataModel([EntitySpec(
            'a', members=[Member('p', Optional(Ref('b')))])])
    with pytest.raises(Error):
        # Ref may not reference flyweights
        DataModel(
            [EntitySpec('a', members=[Member('p', Ref('a_0')), Member('q', uint32())],
                        flyweighted=[FlyweightGroup(members=['q'])],
                        not_flyweighted=['p'])])
    with pytest.raises(Error):
        # empty flyweight
        DataModel([EntitySpec('a', members=[Member('p', uint32())],
                              flyweighted=[FlyweightGroup()],
                              not_flyweighted=['p'])])
    members = [Member('p', uint32()), Member('q', uint32())]
    # ok
    DataModel([EntitySpec('a', members=members,
                          flyweighted=[FlyweightGroup(members=['q'])],
                          not_flyweighted=['p'])])
    for (bad_fw, bad_not_fw) in [
            # missing member in flyweight spec
            ([], ['p']),
            ([FlyweightGroup(members=['q'])], []),
            # unknown member in flyweight spec
            ([FlyweightGroup(members=['q'])], ['p', 'unknown']),
            ([FlyweightGroup(members=['q', 'unknown'])], ['p']),
            # empty flyweight spec
            ([FlyweightGroup(members=['q']), FlyweightGroup()], ['p']),
    ]:
        with pytest.raises(Error):
            # missing member in flyweight spec
            DataModel([EntitySpec('a', members=members,
                                  flyweighted=bad_fw,
                                  not_flyweighted=bad_not_fw)])
    with pytest.raises(Error):
        # name clash
        DataModel([EntitySpec('a'), EntitySpec('a')])

    with pytest.raises(Error):
        # param name clash
        DataModel([EntitySpec('a', members=[Member('p', uint32()),
                                            Member('p', uint32())])])

def test_bad_instance(tmpdir):
    with pytest.raises(Error):
        DataModel([EntitySpec('a')]).serialize(
            hash_to_write=0, a={}, b={})
    with pytest.raises(Error):
        DataModel([EntitySpec('a')]).serialize(hash_to_write=0)

def test_empty(tmpdir):
    tb = TestBench(tmpdir, 'empty0', DataModel(
        [EntitySpec('foo', members=[])]))
    tb.datafile(foo=[{}, {}])
    tb.run_c(f'''
    ASSERT(empty0__num__foo(empty0) == 2);
    empty0_foo_t foo0 = empty0__mk__foo(0);
    empty0_foo_t foo1 = empty0__mk__foo(1);
    ASSERT(memcmp(&foo0, &foo1, sizeof(empty0_foo_t)) != 0);
    ASSERT(empty0__id__foo(foo0) == 0);
    ASSERT(empty0__id__foo(foo1) == 1);
''')

def test_simple(tmpdir):
    tb = TestBench(tmpdir, 'simple_model', DataModel([
        EntitySpec('foo', members=[Member('p', uint32())]),
        EntitySpec('bar', members=[Member('r', Ref('foo')),
                                   Member('o', Optional(Ref('foo')))])]))

    tb.datafile(
        foo=[dict(anchor='foo0', p=4),
             dict(p=5)],
        bar=[dict(r='foo0', o='foo0'),
             dict(r='foo0', o=None)]
    )
    tb.run_c('''
    ASSERT(simple_model__num__foo(simple_model) == 2);
    simple_model_foo_t foo0 = simple_model__mk__foo(0);
    simple_model_foo_t foo1 = simple_model__mk__foo(1);
    ASSERT(simple_model__id__foo(foo0) == 0);
    ASSERT(simple_model__id__foo(foo1) == 1);
    ASSERT(simple_model_foo_p(simple_model, foo0) == 4);
    ASSERT(simple_model_foo_p(simple_model, foo1) == 5);
    ASSERT(simple_model__num__bar(simple_model) == 2);
    simple_model_bar_t bar0 = simple_model__mk__bar(0);
    simple_model_foo_t foo_ref = simple_model_bar_r(simple_model, bar0);
    ASSERT(memcmp(&foo_ref, &foo0, sizeof(simple_model_foo_t)) == 0);
    ASSERT(simple_model_bar_o_valid(simple_model, bar0));
    // optional refs: 0 means nothing, i>0 means the instance with index i-1
    simple_model_foo_t foo_ref2 = simple_model_bar_o(simple_model, bar0);
    ASSERT(memcmp(&foo_ref2, &foo0, sizeof(simple_model_foo_t)) == 0);
    simple_model_bar_t bar1 = simple_model__mk__bar(1);
    ASSERT(!simple_model_bar_o_valid(simple_model, bar1));
    expected_fatal_errors = 1;
    if (setjmp(on_fatal_error) == 0) {
            simple_model_bar_o(simple_model, bar1);
            ASSERT(0);
    } else {
            ASSERT(expected_fatal_errors == 0);
    }
''')

def test_string(tmpdir):
    tb = TestBench(tmpdir, 'str', DataModel([
        EntitySpec('foo', members=[Member('p', String())])]))
    tb.datafile(
        foo=[dict(p=s) for s in ['abc', 'defg', 'abc']])
    tb.run_c('''
    ASSERT(str__num__foo(str) == 3);
    const char *p[] = {
      str_foo_p(str, str__mk__foo(0)),
      str_foo_p(str, str__mk__foo(1)),
      str_foo_p(str, str__mk__foo(2))};
    ASSERT(strcmp(p[0], "abc") == 0);
    ASSERT(strcmp(p[1], "defg") == 0);
    ASSERT(p[2] == p[0]);
''')

def test_list(tmpdir):
    tb = TestBench(tmpdir, 'arr', DataModel([
        EntitySpec('foo', members=[Member('p', List(uint16()))]),
        EntitySpec('bar', members=[Member('r', List(Ref('foo'),
                                                  sz_type=uint8()))])]))
    tb.datafile(
        foo=[dict(anchor='3', p=[3]),
             dict(anchor='45', p=[4, 5])],
        bar=[dict(r=['45', '3'])]
    )
    tb.run_c('''
    ASSERT(arr__num__bar(arr) == 1);
    arr_bar_t bar = arr__mk__bar(0);
    ASSERT(arr_bar_r_len(arr, bar) == 2);
    arr_foo_t foo = arr_bar_r_item(arr, bar, 0);
    ASSERT(arr_foo_p_len(arr, foo) == 2);
    ASSERT(arr_foo_p_item(arr, foo, 0) == 4);
    ASSERT(arr_foo_p_item(arr, foo, 1) == 5);
    foo = arr_bar_r_item(arr, bar, 1);
    ASSERT(arr_foo_p_len(arr, foo) == 1);
    ASSERT(arr_foo_p_item(arr, foo, 0) == 3);
    expected_fatal_errors = 1;
    if (setjmp(on_fatal_error) == 0) {
            arr_foo_p_item(arr, foo, 1);
            ASSERT(0);
    } else {
            ASSERT(expected_fatal_errors == 0);
    }
''')

def test_list_dup(tmpdir):
    '''lists with identical representation share storage'''
    tb = TestBench(tmpdir, 'arr', DataModel([
        EntitySpec('foo', members=[Member('p', List(uint32()))]),
        EntitySpec('bar', members=[Member('r', List(Ref('foo')))])]))
    nodup = tb.datafile('nodup',
        foo=[dict(p=[1, 2, 3, 4]),
             dict(p=[2, 3, 4])],
        bar=[])
    dup = tb.datafile('dup',
        foo=[dict(p=[1, 2, 3, 4]),
             dict(p=[1, 2, 3, 4])],
        bar=[])
    assert len(nodup.read_bytes()) > len(dup.read_bytes())
    nodup2 = tb.datafile('nodup2',
        foo=[dict(anchor='0', p=[0, 1]),
             dict(anchor='1', p=[2, 3, 4])],
        bar=[dict(r=['1', '0'])])
    dup2 = tb.datafile('dup2',
        foo=[dict(anchor='0', p=[0, 1]),
             dict(anchor='1', p=[2, 3, 4])],
        bar=[dict(r=['0', '1'])])
    assert len(nodup2.read_bytes()) > len(dup2.read_bytes())

def test_list_sz_type(tmpdir):
    tb = TestBench(tmpdir, 'sztype', DataModel([
        EntitySpec('u8', members=[
            Member('p', List(uint16(), sz_type=uint8()))]),
        EntitySpec('u64', members=[
            Member('p', List(uint16(), sz_type=uint64()))])]))
    u8sz  = tb.datafile('u8',   u8=[dict(p=[0])] * 10, u64=[]).stat().st_size
    u64sz = tb.datafile('u64', u64=[dict(p=[0])] * 10, u8=[]).stat().st_size
    assert u8sz < u64sz

def test_bool(tmpdir):
    tb = TestBench(tmpdir, 'boolean', DataModel([
        EntitySpec('foo', members=[
            Member(f'p{i}', Bool()) for i in range(9)])]))
    # some more or less random bools; need more than 8 to test
    # deserialization across multiple bytes
    tb.datafile(
        foo=[dict({f'p{i}': False for i in range(7)},
                  p7=j == 0, p8=j == 1) for j in range(2)])
    tb.run_c('''
    ASSERT(boolean__num__foo(boolean) == 2);
    boolean_foo_t foo0 = boolean__mk__foo(0);
    boolean_foo_t foo1 = boolean__mk__foo(1);
    ASSERT(boolean_foo_p7(boolean, foo0));
    ASSERT(!boolean_foo_p7(boolean, foo1));
    ASSERT(!boolean_foo_p8(boolean, foo0));
    ASSERT(boolean_foo_p8(boolean, foo1));
''')

def test_empty_flyweight(tmpdir):
    foo = EntitySpec('foo')
    # this exercises a weird corner in the serialize() logic;
    # zero-length sections don't cause problems

    # Empty flyweights cannot currently be expressed in the API, which
    # arguably makes this test questionable. In any case, we hack them in.
    foo.direct_flyweights = [EntitySpec('foo_0', members=[])]
    tb = TestBench(tmpdir, 'fw', DataModel([foo]))
    tb.datafile(foo=[])
    tb.run_c('''
    ASSERT(fw__num__foo(fw) == 0);
    ''')

def test_flyweight(tmpdir):
    tb = TestBench(tmpdir, 'fw', DataModel(
        [EntitySpec(
            'foo',
            members=[
                Member('p', uint32()),
                Member('a', Bool()),
                Member('b', String()),
                Member('c', List(uint8()))],
            flyweighted=[FlyweightGroup(
                subgroups=[FlyweightGroup(members=['a', 'b', 'c'])])],
            not_flyweighted=['p'])]))

    tb.datafile('empty', foo=[])
    tb.run_c('''
    ASSERT(fw__num__foo(fw) == 0);''', 'empty')
    files = [
        tb.datafile(f'dup{i}', foo=[
            dict(p=j,
                 # fisketur[trivial-cond-exp]
                 a=True if j == (i == 1) else False,
                 b='x' if j == (i == 2) else 'y',
                 c=[1, 2, 4] if j == (i == 3) else [1, 2, 5])
            for j in range(3)])
        for i in range(4)]
    sizes = [f.stat().st_size for f in files]
    # instances 1 and 2 are equal in the first file, and different
    # in subsequent files. Instance 0 differs from both in all instances
    # (and exists to make sure pools are identical)
    assert sizes[0] < sizes[1]
    assert sizes[1] == sizes[2] == sizes[3]
    tb.run_c('''
    ASSERT(fw__num__foo(fw) == 3);
    for (int i = 0; i < 3; i++) {
        ASSERT(fw_foo_p(fw, fw__mk__foo(i)) == i);
    }
    ASSERT(fw_foo_a(fw, fw__mk__foo(0)));
    ASSERT(strcmp(fw_foo_b(fw, fw__mk__foo(0)), "x") == 0);
    ASSERT(fw_foo_c_item(fw, fw__mk__foo(0), 2) == 4);
    for (int i = 1; i < 3; i++) {
        ASSERT(!fw_foo_a(fw, fw__mk__foo(i)));
        ASSERT(strcmp(fw_foo_b(fw, fw__mk__foo(i)), "y") == 0);
        ASSERT(fw_foo_c_item(fw, fw__mk__foo(i), 2) == 5);
    }
''', datafile='dup0')

def test_flyweight_bool(tmpdir):
    tb = TestBench(tmpdir, 'fw', DataModel(
        [EntitySpec(
            'foo', members=[
                Member('a', Bool()), Member('b', uint8())],
            flyweighted=[FlyweightGroup(members=['a', 'b'])],
            not_flyweighted=[])]))
    tb.datafile(foo=[{'a': i % 2, 'b': i} for i in range(20)])
    tb.run_c('''
        ASSERT(fw_foo_a(fw, fw__mk__foo(15)));
        ASSERT(fw_foo_b(fw, fw__mk__foo(15)) == 15);
        ASSERT(!fw_foo_a(fw, fw__mk__foo(16)));
        ASSERT(fw_foo_b(fw, fw__mk__foo(16)) == 16);
    ''')

def test_shared_flyweight(tmpdir):
    # Previous versions of the API permitted declaring flyweights
    # shared between entities, and the mechanics to support this in
    # the serialization infrastructure has a low maintenance
    # cost. However, this kind of sharing cannot be expressed within
    # the current API, so in order to unit test these aspects we need
    # to patch some internals a bit
    foo_0_0_members = [Member('c', uint16())]
    foo = EntitySpec('foo', members=[Member('a', uint16()),
                                     Member('b', uint16())] + foo_0_0_members,
                     flyweighted=[FlyweightGroup(
                         members=['a'],
                         subgroups=[FlyweightGroup(members=['c'])])],
                     not_flyweighted=['b'])
    bar = EntitySpec('bar', members=[Member('a', uint16()),
                                     Member('b', uint16())] + foo_0_0_members,
                     flyweighted=[FlyweightGroup(
                         members=['b'],
                         subgroups=[FlyweightGroup(members=['c'])])],
                     not_flyweighted=['a'])
    dm = DataModel([foo, bar])
    foo_a_fw = foo.direct_flyweights[0]
    bar_b_fw = bar.direct_flyweights[0]
    assert foo_a_fw.direct_members[0].name == 'a'
    assert bar_b_fw.direct_members[0].name == 'b'
    bar_b_fw.direct_flyweights[0] = foo_a_fw.direct_flyweights[0]
    tb = TestBench(tmpdir, 'fw', dm)
    conf = dict(
        foo=[dict(a=1, b=3, c=5),
             dict(a=2, b=3, c=5)],
        bar=[dict(a=1, b=4, c=5),
             dict(a=2, b=3, c=6)])
    tb.datafile(**conf)
    tb.run_c(
        '\n  '.join(
            f'ASSERT(fw_{name}_{member}(fw, fw__mk__{name}({i})) == {value});'
            for (name, instances) in conf.items()
            for (i, instance) in enumerate(instances)
            for (member, value) in instance.items()),
        linemarks=False)

def test_diamond_flyweights(tmpdir):
    foo = EntitySpec('foo',
                     members=[Member('a', uint16()),
                              Member('b', uint16()),
                              Member('c', uint16())],
                     flyweighted=[
                         FlyweightGroup(members=['a'],
                                        subgroups=[FlyweightGroup(['c'])]),
                         FlyweightGroup(members=['b'],
                                        # current input format doesn't permit
                                        # a diamond structure; patching
                                        # manually below instead
                                        #subgroups=[FlyweightGroup(['c'])]
                                        )],
                     not_flyweighted=[])
    dm = DataModel([foo])
    [a_fw, b_fw] = foo.direct_flyweights
    [c_fw] = a_fw.direct_flyweights
    assert len(b_fw.direct_flyweights) == 0
    b_fw.direct_flyweights = [c_fw]
    b_fw.transitive_members.extend(c_fw.direct_members)
    tb = TestBench(tmpdir, 'fw', dm)

    foos = [
        dict(a=1, b=3, c=5),
        dict(a=2, b=3, c=5),
        dict(a=1, b=4, c=5),
        dict(a=2, b=3, c=6)]

    tb.datafile(foo=foos)
    tb.run_c(
        '\n  '.join(
            f'ASSERT(fw_foo_{member}(fw, fw__mk__foo({i})) == {value});'
            for (i, instance) in enumerate(foos)
            for (member, value) in instance.items()),
        linemarks=False)
