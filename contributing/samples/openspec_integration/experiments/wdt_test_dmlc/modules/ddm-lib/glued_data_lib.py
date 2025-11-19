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

import sys
import os
import abc
from dataclasses import dataclass, KW_ONLY
from pathlib import Path
import typing
import functools
import operator
import re
from io import BytesIO
import difflib
import yaml
from simicsutils.host import host_type
from glue_config import GlueConfig, GlueConfigFromYaml
import glue_config

__all__ = ['glue_body', 'deduce_expr', 'deduce_config_expr',
           'resource_hash', 'glue_header', 'process_glue_and_data',
           'GlueConfig', 'GlueConfigFromYaml']

class Error(glue_config.Error):
    def __init__(self, msg, config=None):
        super().__init__(msg, linemark=config and config.linemark)

def flatten_tree(tree):
    if isinstance(tree, str):
        yield tree
    else:
        for sub in tree:
            yield from flatten_tree(sub)

def test_flatten_tree():
    assert list(flatten_tree('x')) == ['x']
    assert list(flatten_tree([['x', 'y'], ['z', 'w']])) == ['x', 'y', 'z', 'w']

def deep_map(fun, elems):
    if isinstance(elems, list):
        return [deep_map(fun, elem) for elem in elems]
    else:
        return fun(elems)

def test_deep_map():
    assert deep_map(lambda x: x + 4, 3) == 7
    assert deep_map(lambda x: x + 4, [3, 5]) == [7, 9]
    assert deep_map(lambda x: x + 4, [[3, 5], [9], []]) == [[7, 9], [13], []]

class Expr(abc.ABC):
    # outermost indices first
    @abc.abstractmethod
    def str(self, indexvars: list[str]) -> str:
        pass
    @abc.abstractmethod
    def eval(self, indices: list[int]) -> int:
        pass

@dataclass
class LinearExpr:
    # elem 0 is constant coeff, elem 1 is coeff for innermost dim variable.
    # Missing outer dims are assumed to be zero.
    coeffs: tuple
    def __init__(self, coeffs):
        self.coeffs = tuple(coeffs)

    def str(self, indexvars):
        mask = (1 << 64) - 1
        return f'0x{self.coeffs[0] & mask:x}' + ''.join(
            f' + {coeff & mask} * {var}'
            for (var, coeff) in zip(reversed(indexvars), self.coeffs[1:])
            if coeff)

    def eval(self, indices):
        '''mainly for test'''
        return sum((i * coeff for (i, coeff) in zip(reversed(indices),
                                                    self.coeffs[1:])),
                   self.coeffs[0]) & ((1 << 64) - 1)

@dataclass
class CondExpr:
    # reverse indexed, 1 is innermost dim variable
    dim: int
    # pick right tree if dim variable >= pivot
    pivot: int
    left: Expr
    right: Expr

    def str(self, indexvars):
        return (f'{indexvars[-self.dim]} < {self.pivot}'
                f' ? {self.left.str(indexvars)} : {self.right.str(indexvars)}')

    def eval(self, indices):
        return (self.left.eval(indices) if indices[-self.dim] < self.pivot
                else self.right.eval(indices))

def bisection_tree(dim_id: int, exprs: list[(int, Expr)]) -> Expr:
    if len(exprs) == 1:
        [(i, tree)] = exprs
        return tree
    else:
        half = len(exprs) // 2
        left = exprs[:half]
        right = exprs[half:]
        (pivot, _) = right[0]
        return CondExpr(dim_id, pivot,
                        bisection_tree(dim_id, left),
                        bisection_tree(dim_id, right))

def deduce_config_expr(conf, f):
    return deduce_expr(conf.dimsizes, deep_map(f, conf.anchor))

def deduce_expr(dims: list[int], values) -> Expr:
    '''Given an exploded n-dim list of values, deduce a closed expression'''
    if dims:
        dimsize = dims[0]
        assert dimsize
        assert len(values) == dimsize
        subtrees = [(i, deduce_expr(dims[1:], v))
                    for (i, v) in enumerate(values)]
        (_, first_subtree) = subtrees[0]
        collapsed = [(
            0,
            LinearExpr(first_subtree.coeffs + (0,))
            if isinstance(first_subtree, LinearExpr) else first_subtree)]
        for (i, subtree) in subtrees[1:]:
            (last_i, last_tree) = collapsed[-1]
            if isinstance(subtree, LinearExpr):
                subtree = LinearExpr(subtree.coeffs + (0,))
                if (isinstance(last_tree, LinearExpr)
                    and subtree.coeffs[1:len(dims)]
                    == last_tree.coeffs[1:len(dims)]):
                    if i == last_i + 1:
                        i_coeff = subtree.coeffs[0] - last_tree.coeffs[0]
                        collapsed[-1] = (last_i, LinearExpr(
                            (last_tree.coeffs[0] - i_coeff * last_i,)
                            + last_tree.coeffs[1:len(dims)]
                            + (i_coeff,)))
                    else:
                        i_coeff = last_tree.coeffs[len(dims)]
                        if (last_tree.coeffs[0] + i_coeff * (i - last_i)
                            != subtree.coeffs[0]):
                            collapsed.append((i, subtree))
                else:
                    collapsed.append((i, subtree))
            else:
                if subtree == last_tree:
                    # consecutive identical expressions
                    # e.g. common for field array LSBs across reg arrays
                    pass
                else:
                    collapsed.append((i, subtree))
        tree = bisection_tree(len(dims), collapsed)
        return tree
    else:
        assert isinstance(values, int)
        return LinearExpr((values,))

def test_deduce_expr():
    from random import randrange
    assert deduce_expr([], 15).str([]) == '0xf'
    assert deduce_expr([1], [3]).str(['i']) == '0x3'
    assert deduce_expr([2], [3, 3]).str(['i']) == '0x3'
    assert deduce_expr([2], [3, 7]).str(['i']) == '0x3 + 4 * i'
    assert deduce_expr([3], [3, 7, 11]).str(['i']) == '0x3 + 4 * i'
    assert (deduce_expr([3], [3, 7, 10]).str(['i'])
            == 'i < 2 ? 0x3 + 4 * i : 0xa')
    assert (deduce_expr([2, 3], [[3, 7, 10], [3, 7, 10]]).str(['j', 'i'])
            == 'i < 2 ? 0x3 + 4 * i : 0xa')
    assert (deduce_expr([2, 3], [[3, 7, 10], [3, 7, 11]]).str(['j', 'i'])
            == 'j < 1 ? i < 2 ? 0x3 + 4 * i : 0xa : 0x3 + 4 * i')
    dimsizes = [randrange(2, 5) for _ in range(3)]
    coeffs = [randrange(1000000) for _ in range(4)]
    values = [[[coeffs[0] + x * coeffs[3] + y * coeffs[2] + z * coeffs[1]
                for z in range(dimsizes[2])]
               for y in range(dimsizes[1])]
              for x in range(dimsizes[0])]
    assert (deduce_expr(dimsizes, values).str(['x' , 'y', 'z'])
            == f'0x{coeffs[0]:x} + {coeffs[1]} * z + {coeffs[2]} * y'
            f' + {coeffs[3]} * x'), values
    coord = list(map(randrange, dimsizes))
    values[coord[0]][coord[1]][coord[2]] += 1
    not_linear = deduce_expr(dimsizes, values)
    assert isinstance(not_linear, CondExpr)
    for (x, ys) in enumerate(values):
        for (y, zs) in enumerate(ys):
            for (z, value) in enumerate(zs):
                assert not_linear.eval([x, y, z]) == value


def get_close_matches_case_insensitive(needle, haystack, *args):
    lowered = {s.lower(): s for s in haystack}
    return [lowered[s]
            for s in difflib.get_close_matches(needle.lower(), lowered, *args)]


class InvalidAnchorError(Error):
    def __init__(self, config: GlueConfig,
                 anchor: str, valid_anchors: list[str]):
        msg = f'Invalid {config.entity_type} anchor {anchor} in glue config'
        super().__init__(msg, config)
        self.anchor = anchor
        self.valid_anchors = valid_anchors

    def __str__(self):
        [msg] = self.args
        close = get_close_matches_case_insensitive(self.anchor, self.valid_anchors)
        if close:
            msg += f'. Did you mean {" or ".join(close)}?'
        return self.linemark_prefix(msg)

def dml_tree_from_config(dia_name, name, config, data, mapped_anchors, indent):
    array_suffix = ''.join(f'[{v} < {sz}]' for (v, sz) in config.dims[
        len(config.dims) - config.num_local_dims:])
    if config.anchor is None:
        yield f'{indent}{config.object_type} {name}{array_suffix} {{'
        # TODO if this is a register, set its init_val based on that of
        # anchored fields.
        # This isn't necessary for init or resets to work
        # (see the config.object_type == 'field' path),
        # but having a correct init_val matters for any other code referencing
        # it.
    else:
        assert config.entity_type in data, config.entity_type
        idx = len(mapped_anchors.setdefault(config.entity_type, {}))
        anchors = list(flatten_tree(config.anchor))
        for anchor in anchors:
            if anchor not in data[config.entity_type]:
                raise InvalidAnchorError(
                    config, anchor, data[config.entity_type])
            elif anchor in mapped_anchors[config.entity_type]:
                # TODO: blame culprit
                raise Error(f"The {config.entity_type} '{anchor}' is used as "
                            + "an anchor multiple times")

            mapped_anchors[config.entity_type][anchor] = None
        params = [f'param first_{config.entity_type}_index = {idx};']
        if config.object_type == 'field':
            lsbs = deep_map(lambda anchor: data['field'][anchor]['lsb'],
                            config.anchor)
            def msb_from_anchor(anchor):
                field = data['field'][anchor]
                return field['lsb'] + field['bitsize'] - 1
            msbs = deep_map(msb_from_anchor, config.anchor)
            (dimvars, dimsizes) = (map(list, zip(*config.dims))
                                   if config.dims else ([], []))
            lsb_expr = deduce_expr(dimsizes, lsbs)
            msb_expr = deduce_expr(dimsizes, msbs)
            parent_reg_glued = all(
                data['field'][anchor]['reg'] in mapped_anchors['reg']
                for anchor in anchors)
            if parent_reg_glued:
                suffix = (f' @ [{msb_expr.str(dimvars)} : '
                          + f'{lsb_expr.str(dimvars)}]')
            else:
                # msb/lsb intentionally not defined. When the parent reg's
                # unglued, the msb/lsb of the DDM fields may have nothing to
                # do with where the modeller wants their storage to be in the
                # DML register, so they have to specify it manually within DML
                #
                # TODO consider supporting msb/lsb specification from glue.
                # This has a small number of benefits, such as allowing common
                # code for the field to work regardless of whether the register
                # is anchored (*most of the time*), and moving the bitsize
                # consistency check of DML field vs. the DDM field it anchors
                # from module load to build time.
                #
                # Re. "most of the time:" glued fields under a glued register
                # vs. an unglued register differ quite significantly,
                # semantically, especially re. how the storage of the register
                # is used and write_register semantics. This may force changes
                # in the DML code anyway.
                suffix = ''

                # If the parent register isn't glued, then it won't get an
                # automatic init_val definition, which will break
                # initialization and resets. Defining init_val on a
                # per-anchored field level fixes that.
                def init_val_from_anchor(anchor):
                    field = data['field'][anchor]
                    reg_init_val = data['reg'][field['reg']]['init_val']
                    return ((reg_init_val >> field['lsb'])
                            & ((1 << field['bitsize']) - 1))
                init_val_expr = deduce_config_expr(config,
                                                   init_val_from_anchor)
                params.append(
                    f'param init_val = {init_val_expr.str(dimvars)};')
        elif config.object_type == 'register':
            sizes = {data['reg'][anchor]['size']
                     for anchor in anchors}
            if len(sizes) != 1:
                raise Error(
                    'Inconsistent sizes across indices'
                    f' in register array {name}', config=config)
            (size,) = sizes
            suffix = f' size {size}'
            init_vals = deep_map(lambda anchor: data['reg'][anchor]['init_val'],
                                 config.anchor)
            (dimvars, dimsizes) = (map(list, zip(*config.dims))
                                   if config.dims else ([], []))
            init_val_expr = deduce_expr(dimsizes, init_vals)
            params.append(f'param init_val = {init_val_expr.str(dimvars)};')
        else:
            suffix = ''
        decl = f'{indent}{config.object_type} {name}{array_suffix}{suffix}'
        templates = [f'{dia_name}_assoc_to_{config.entity_type}']
        if (config.object_type in {'register', 'field'}
            and config.entity_type in {'reg', 'field'}):
            templates.append(
                f'ddm_assoc_{config.object_type}_to_{config.entity_type}')
        yield (f'{decl} is ({", ".join(templates)}) {{')
        for param in params:
            yield f'{indent}    {param}'

    for (subname, subconfig) in config.sub.items():
        yield from dml_tree_from_config(
            dia_name, subname, subconfig, data, mapped_anchors,
            f'{indent}    ')
    yield f'{indent}}}'

def glue_body(dia_name: str, glue_config: "GlueConfig",
              data: dict[str, dict[str, dict[str, object]]]
              ) -> (str, dict[str, list[str]]):
    # Order matters to ensure consistent generated glue, thus dict[str, None]
    # rather than set[str]
    mapped_anchors: dict[str, dict[str, None]] = {}
    assert glue_config.object_type == 'device'
    assert not glue_config.dims
    assert not glue_config.anchor
    dml_decls = ''.join(
        f'{line}\n'
        for (name, sub) in glue_config.sub.items()
        for line in dml_tree_from_config(
            dia_name, name, sub,
            data, mapped_anchors, ""))

    return (dml_decls, mapped_anchors)


def resource_hash(
        data: dict[str, dict[str, dict[str, object]]]):
    return hash(tuple(
        functools.reduce(operator.xor, (hash((i, anchor)) for (i, anchor)
                                        in enumerate(instances)), 0)
        for instances in data.values()))


def glue_header(resource_name: str, dia_name: str, resource_hash: int):
    return rf'''
dml 1.4;

header %{{
    static __attribute__((noinline)) bytes_t _ddm_{resource_name}(void) {{
        bytes_t ret;
        asm volatile (
            ".section .rodata\n"
            ".align 8\n"
            "_{resource_name}_data_start:\n"
            ".incbin \"{resource_name}\"\n"
            "_{resource_name}_data_end:\n"
            ".text\n"
            "leaq _{resource_name}_data_start(%%rip), %0\n"
            "movq $(_{resource_name}_data_end - _{resource_name}_data_start),"
                " %1\n"
            : "=r" (ret.data), "=r" (ret.len)
        );
        return ret;
    }}
%}}
extern bytes_t _ddm_{resource_name}(void);

group {dia_name} is ddm_dialect_base {{
    param ddmdef_resource = _ddm_{resource_name};
    param ddmdef_resource_hash = {resource_hash};
}}
'''

def validate_regs(data):
    all_regs = data['reg']
    for (bname, b) in data['bank'].items():
        offsets = [(all_regs[rname]['offset'],
                    all_regs[rname]['size']) for rname in b['regs']]
        for ((o1, s1), (o2, _)) in zip(offsets, offsets[1:]):
            if o1 > o2:
                raise Error(f'Registers not sorted by offset in bank {bname}')
            # if o2 < o1 + s1:
            #     msg = 'Overlapping registers in bank'
            #     msg += f'{bname}@{hex(o1)} involving registers:'
            #     for rname in b['regs']:
            #         if all_regs[rname]['offset'] in {o1, o2}:
            #             msg += f' {rname}'
            #     raise Error(msg)

def process_glue_and_data(resource_name: str, dia_name: str, dm: "DataModel",
                          glue_config: "GlueConfig",
                          data: dict[str, dict[str, dict[str, object]]],
                          blob_path: Path | None = None,
                          ) -> str:
    assert re.match('^[A-Za-z_][A-Za-z0-9_]*$', resource_name)
    assert re.match('^[A-Za-z_][A-Za-z0-9_]*$', dia_name)
    if blob_path is None:
        # This branch is only for compat with currently existing calls
        blob_path = Path(resource_name)
    rhash = resource_hash(data)
    validate_regs(data)
    dml_header = glue_header(resource_name, dia_name, rhash)
    (dml_body, glue_record) = glue_body(dia_name, glue_config, data)

    for m in dm.entity_specs['handles'].transitive_members:
        glue_record.setdefault(m.name, [])
    data = dm.serialize(rhash, handles={'': glue_record}, **data)
    blob_path.write_bytes(data)

    return dml_header + dml_body
