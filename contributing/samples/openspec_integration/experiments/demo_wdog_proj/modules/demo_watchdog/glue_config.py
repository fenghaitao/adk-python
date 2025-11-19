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

import re
import typing
from dataclasses import dataclass, KW_ONLY
from pathlib import Path
import yaml

class Error(Exception):
    def __init__(self, msg, linemark: typing.Optional[yaml.Mark]=None):
        super().__init__(msg)
        self.linemark = linemark

    def linemark_prefix(self, msg):
        if self.linemark:
            return (f'{self.linemark.name}:{self.linemark.line + 1}'
                    f':{self.linemark.column}: error: {msg}')
        return msg

    def __str__(self):
        return self.linemark_prefix(super().__str__())

objtypes = ['subdevice', 'bank', 'group', 'port', 'implement', 'interface',
            'register', 'field', 'attribute', 'connect', 'event']
ident = '[a-zA-Z_][a-zA-Z0-9_]*'
number = '(?:0x[0-9a-fA-F]+)|0|(?:[1-9][0-9]*)'
arr = f'\\[({ident}) *< *({number})\\]'
key_re = re.compile('(' + '|'.join(objtypes) + f') ({ident})((?:{arr})*)$')
arr_re = re.compile(arr)
def test_re():
    for s in ['Z', 'a_Z92', '_4']:
        assert re.match(f'({ident})', s).groups() == (s,)
    for bad in ['', '3']:
        assert re.match(ident, bad) is None
    for s in ['0', '473', '0x02fE3']:
        assert re.match(f'({number})', s).groups() == (s,)
    assert re.match(f'({number})', '234e').groups() == ('234',)
    assert re.match(f'({number})', '0x').groups() == ('0',)
    assert re.match(f'({number})', '01').groups() == ('0',)
    assert re.match(f'({number})', '') is None
    assert re.match(arr, '[idx < 10]').groups() == ('idx', '10')
    assert (key_re.match('bank b[i < 10][j<0x4]').groups()[:3]
            == ('bank', 'b', '[i < 10][j<0x4]'))
    assert key_re.match('bank b ') is None
    assert ([m.groups() for m in arr_re.finditer('[i < 10][j<0x4]')]
            == [('i', '10'), ('j', '0x4')])

def expand_anchor(prefix: str, anchor: str, dims: list[(str, int)],
                  idxvars: dict[str, int]):
    if isinstance(anchor, str):
        if dims:
            (name, sz) = dims[0]
            idxvars = dict(idxvars)
            ret = []
            for i in range(sz):
                idxvars[name] = i
                ret.append(expand_anchor(prefix, anchor, dims[1:], idxvars))
            return ret
        else:
            return prefix + anchor.format(**idxvars)
    else:
        assert isinstance(anchor, list)
        if not dims:
            raise Error(f'Too deeply nested anchor list: {anchor}')
        (name, sz) = dims[0]
        if len(anchor) != sz:
            raise Error('Wrong size of anchor array:'
                        f' dimension {name} has size {sz}, got {anchor}')
        idxvars = dict(idxvars)
        ret = []
        for (sub, i) in zip(anchor, range(sz)):
            idxvars[name] = i
            ret.append(expand_anchor(prefix, sub, dims[1:], idxvars))
        return ret

def test_expand_anchor():
    import pytest
    assert expand_anchor('p', 'a', [], {}) == 'pa'
    assert expand_anchor('p', 'a{i}', [], {'i': 1}) == 'pa1'
    assert expand_anchor('p', 'a{i}', [('i', 2)], {}) == ['pa0', 'pa1']
    assert expand_anchor('p', ['a{i}_{j}', 'b{i}_{j}'], [('j', 2)],
                         {'i': 1}) == ['pa1_0', 'pb1_1']
    with pytest.raises(Error):
        expand_anchor('', ['a{i}', 'b{i}'], [], {'i': 1})
    with pytest.raises(Error):
        expand_anchor('', ['a{i}', 'b{i}'], [('j', 3)], {'i': 1})
    assert expand_anchor('', 'a{i}_{j}', [('i', 2), ('j', 2)], {}) == [
        ['a0_0', 'a0_1'], ['a1_0', 'a1_1']]

def expand_prefixed_anchor(
        prefixes, prefix_dims, anchors, local_dims, idxvars):
    if prefix_dims:
        (name, sz) = prefix_dims[0]
        assert isinstance(prefixes, list) and len(prefixes) == sz
        idxvars = dict(idxvars)
        ret = []
        for (i, sub) in enumerate(prefixes):
            idxvars[name] = i
            ret.append(expand_prefixed_anchor(sub, prefix_dims[1:],
                                              anchors, local_dims, idxvars))
        return ret
    else:
        assert isinstance(prefixes, str)
        return expand_anchor(prefixes, anchors, local_dims, idxvars)

def test_expand_prefixed_anchor():
    assert expand_prefixed_anchor('a', [], 'b', [], {}) == 'ab'
    # inner call is an expand_anchor
    assert expand_prefixed_anchor(
        '', [], 'a{i}_{j}', [('i', 2), ('j', 2)], {}) == [
        ['a0_0', 'a0_1'], ['a1_0', 'a1_1']]
    # prefix is prepended structurally, and
    assert expand_prefixed_anchor(['x', 'y'], [('i', 2)], 'b{i}', [], {}) == [
        'xb0', 'yb1']
    assert expand_prefixed_anchor(
        [['a', 'b'], ['c', 'd']], [('i', 2), ('j', 2)],
        '{i}x{j}', [], {}) == [
        ['a0x0', 'b0x1'], ['c1x0', 'd1x1']]
    assert expand_prefixed_anchor(
        ['a', 'b'], [('i', 2)], ['c', 'd'], [('j', 2)], {}) == [
        ['ac', 'ad'], ['bc', 'bd']]

def add_suffix(tree, suffix):
    if isinstance(tree, str):
        return tree + suffix
    else:
        return [add_suffix(child, suffix) for child in tree]

def test_add_suffix():
    assert add_suffix('a', 'x') == 'ax'
    assert add_suffix([['a', 'b'], 'c'], 'x') == [['ax', 'bx'], 'cx']


class LineInfoLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        assert 'linemark' not in mapping
        mapping['linemark'] = node.start_mark
        return mapping

@dataclass
class GlueConfig:
    # the DML object type to generate
    object_type: str
    # the EntitySpec the anchor refers to. Usually coincides with
    # object_type, except register vs reg.
    entity_type: typing.Optional[str]
    dims: list[(str, int)]
    num_local_dims: int
    anchor: typing.Union[str, list, None]
    sub: dict[str, "GlueConfig"]
    _: KW_ONLY
    linemark: typing.Optional[yaml.Mark] = None

    @staticmethod
    def from_yaml(path: Path):
        with open(path, 'r') as f:
            loader = LineInfoLoader(f)
            toplevel = loader.get_single_data()
        return GlueConfig.from_yaml_tree(toplevel)

    @staticmethod
    def from_yaml_tree(toplevel: dict):
        return GlueConfigFromYaml._from_yaml_subtree(
            'device', '', toplevel, [], [], '')

    @property
    def dimvars(self):
        return [t[0] for t in self.dims]

    @property
    def dimsizes(self):
        return [t[1] for t in self.dims]

    def dml_node_decl(self, name):
        array_suffix = ''.join(f'[{v} < ...]' for (v, _) in self.dims[
            len(self.dims) - self.num_local_dims:])
        return f'{self.object_type} {name}{array_suffix}'

def _decode_children(body):
    for (key, value) in body.items():
        if ' ' in key:
            dml_decl_match = key_re.match(key)
            if dml_decl_match is None:
                raise Error(f"syntax error: {key}")
            (objtype, name, array_str) = dml_decl_match.groups()[:3]
            local_dims = [(idxvar, int(size))
                          for (idxvar, size) in arr_re.findall(array_str)]
            yield (objtype, name, local_dims, value)

@dataclass
class GlueConfigFromYaml(GlueConfig):
    sub: dict[str, "GlueConfigFromYaml"]
    extra_props: dict[str, object]

    @staticmethod
    def _from_yaml_subtree(
            objtype, name, structure: typing.Optional[dict],
            parent_dims, local_dims, anchor_prefixes):
        if structure is None:
            return GlueConfigFromYaml(objtype, None, parent_dims + local_dims,
                                      len(local_dims), None, {}, {})
        try:
            linemark = structure.get('linemark')
            rectype = structure.get('anchor_type',
                                    {'register': 'reg'}.get(objtype, objtype))
            dims = parent_dims + local_dims
            anchor_qualified = structure.get('anchor_qualified')
            anchor = structure.get('anchor')
            if anchor is not None:
                if anchor_qualified is not None:
                    raise Error("cannot define both anchor and"
                                " anchor_qualified in the same object",
                                linemark=linemark)
                anchor_qualified = expand_prefixed_anchor(
                    anchor_prefixes, parent_dims, anchor, local_dims, {})
            elif anchor_qualified is not None:
                anchor_qualified = expand_anchor('', anchor_qualified, dims, {})

            anchor_prefix_qualified = structure.get('anchor_prefix_qualified')
            anchor_prefix = structure.get('anchor_prefix')
            if anchor_prefix_qualified is not None:
                if anchor is not None:
                    raise Error(f"{name}: cannot define both anchor and"
                                " anchor_prefix_qualified in the same object",
                                linemark=linemark)
                anchor_prefix_qualified = expand_anchor(
                    '', anchor_prefix_qualified, dims, {})
            elif anchor_prefix is None and anchor_qualified:
                anchor_prefix_qualified = anchor_qualified
            else:
                if anchor_prefix is None:
                    indices = ''.join(f'[{{{var}}}]' for (var, _) in local_dims)
                    anchor_prefix = (f'{name}{indices}' if anchor_prefixes == ''
                                     else f'.{name}{indices}')
                anchor_prefix_qualified = expand_prefixed_anchor(
                    anchor_prefixes, parent_dims, anchor_prefix, local_dims, {})
            extra_props = {key: val for (key, val) in structure.items()
                           if key not in {
                                   'anchor', 'anchor_qualified', 'anchor_prefix',
                                   'anchor_prefix_qualified', 'anchor_type',
                                   'linemark'}
                           and ' ' not in key}

            return GlueConfigFromYaml(
                objtype,
                rectype,
                dims,
                len(local_dims),
                anchor_qualified,
                {name: GlueConfigFromYaml._from_yaml_subtree(
                        objtype, name, {} if body is None else body,
                        dims, local_dims, anchor_prefix_qualified)
                    for (objtype, name, local_dims, body)
                    in _decode_children(structure)},
                extra_props,
                linemark=linemark)
        except Error as e:
            if e.linemark is None and linemark is not None:
                e.linemark = linemark
            print(e)
            raise
        except Exception as e:
            raise Error(f'Error expanding glue config: {e}',
                        linemark=linemark) from e

def test_from_yaml_tree():
    class OMITTED: pass
    def gc(object_type='group', entity_type=OMITTED,
           dims=[], num_local_dims=0, anchor=None,
           sub={}, linemark=None, extra_props={}):
        if entity_type is OMITTED:
            entity_type = object_type
        return GlueConfigFromYaml(
            object_type=object_type, entity_type=entity_type,
            dims=dims, num_local_dims=num_local_dims, anchor=anchor,
            sub=sub, linemark=linemark, extra_props=extra_props)
    assert GlueConfig.from_yaml_tree({}) == gc(object_type='device')
    assert GlueConfig.from_yaml_tree({'anchor': 'x'}) == gc(
        object_type='device', anchor='x')
    assert GlueConfig.from_yaml_tree({'bar': 'z'}) == gc(
        object_type='device', extra_props={'bar': 'z'})
    assert GlueConfig.from_yaml_tree({'group foo': {'anchor': 'x'}}).sub == {
        'foo': gc(anchor='x')}
    assert GlueConfig.from_yaml_tree(
        {'group foo[i<2]': {'anchor': 'x{i}'}}).sub == {
            'foo': gc(dims=[('i', 2)], num_local_dims=1,
                      anchor=['x0', 'x1'])}
    assert GlueConfig.from_yaml_tree(
        {'group foo[i<2]': {
            'group bar': {'anchor': '.x'}}}).sub == {
                'foo': gc(
                    dims=[('i', 2)], num_local_dims=1, sub={
                        'bar': gc(dims=[('i', 2)],
                                  anchor=['foo[0].x', 'foo[1].x'])})}
    assert GlueConfig.from_yaml_tree(
        {'group foo': {
            'group bar[i<2]': {
                'group baz': {
                    'anchor': '.x'}}}}).sub == {
                        'foo': gc(sub={
                            'bar': gc(dims=[('i', 2)], num_local_dims=1, sub={
                                'baz': gc(dims=[('i', 2)],
                                          anchor=['foo.bar[0].x',
                                                  'foo.bar[1].x'])})})}
    assert GlueConfig.from_yaml_tree(
        {'group foo': {
            'anchor_prefix': '',
            'group bar': {
                'group baz': {'anchor': '.x'}}}}).sub == {
                    # bar.x, not .bar.x, because anchor prefix is empty
                    'foo': gc(sub={'bar': gc(sub={'baz': gc(anchor='bar.x')})})}
    assert GlueConfig.from_yaml_tree(
        {'group foo[i<2]': {
            'anchor_prefix': 'y',
            'group bar[j<2]': {'anchor': 'x{i}{j}'}}}).sub == {
            'foo': gc(dims=[('i', 2)], num_local_dims=1, sub={
                'bar': gc(dims=[('i', 2), ('j', 2)],
                          num_local_dims=1,
                          anchor=[['yx00', 'yx01'], ['yx10', 'yx11']])})}
    assert GlueConfig.from_yaml_tree(
        {'group foo[i<2]': {
            'group bar[j<2]': {
                'anchor_qualified': [['a', 'b'], ['c', 'd']]}}}).sub == {
            'foo': gc(dims=[('i', 2)], num_local_dims=1, sub={
                'bar': gc(dims=[('i', 2), ('j', 2)],
                          num_local_dims=1,
                          anchor=[['a', 'b'], ['c', 'd']])})}
    assert GlueConfig.from_yaml_tree(
        {'group foo[i<2]': {
            'group bar[j<2]': {'anchor_qualified': 'y{j}{i}'}}}).sub == {
            'foo': gc(dims=[('i', 2)], num_local_dims=1, sub={
                'bar': gc(dims=[('i', 2), ('j', 2)],
                          num_local_dims=1,
                          anchor=[['y00', 'y10'], ['y01', 'y11']])})}
    assert (
        GlueConfig.from_yaml_tree({'group a[i<2]': {
            'anchor_prefix_qualified': 'a{i}',
            'group b[j<2]': {
                'anchor': '.b{j}'
            },
            'group c[j<2]': {
                'anchor_prefix_qualified': '',
                'group d': {
                    'anchor': 'd{i}{j}'
                }
            },
            'group e': {
                'anchor_prefix_qualified': ['x', 'y'],
                'group f': {
                    'anchor': '.f'
                }}}}).sub
        == {
            'a': gc(dims=[('i', 2)], num_local_dims=1, sub={
                'b': gc(dims=[('i', 2), ('j', 2)], num_local_dims=1,
                        anchor=[['a0.b0', 'a0.b1'], ['a1.b0', 'a1.b1']]),
                'c': gc(dims=[('i', 2), ('j', 2)], num_local_dims=1,
                        sub={'d': gc(dims=[('i', 2), ('j', 2)],
                                     anchor=[['d00', 'd01'], ['d10', 'd11']])}),
                'e': gc(dims=[('i', 2)], sub={
                    'f': gc(dims=[('i', 2)], anchor=['x.f', 'y.f'])
                })})})

def test_from_yaml(tmpdir):
    import pytest
    def error_on_line(i, body):
        path = tmpdir / 'test.yaml'
        path.write_text(body, 'utf-8')
        with pytest.raises(Error) as e:
            GlueConfig.from_yaml(path)
        assert f'test.yaml:{i}:' in str(e.value)
    error_on_line(2, '''
foo bar:
''')
    error_on_line(3, '''
group bar:
    anchor: x
    anchor_qualified: x
''')
    error_on_line(3, '''
group bar:
    anchor: x
    anchor_prefix_qualified: x
''')
    error_on_line(3, '''
group bar[i<2]:
    anchor_qualified: [x]
''')
    error_on_line(3, '''
group bar[i<2]:
    anchor: foo{j}
''')
    error_on_line(3, '''
group bar[i<2]:
    anchor_prefix_qualified: foo{j}
''')
