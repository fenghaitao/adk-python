#!/usr/bin/env python

# INTEL CONFIDENTIAL

# © 2019 Intel Corporation
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
import sys
import argparse
import xml.etree.ElementTree as etree
from pathlib import Path
from typing import Callable, Optional, Union
from dataclasses import dataclass
import dataclasses

from model_spec import dm

sys.path.append(str(Path(__file__).parent.parent / 'ddm-cmn-common'))
from glued_data_lib import process_glue_and_data
from glue_config import GlueConfig

reserved_names = {'set': 'Set',
                  'size': 'Size',
                  'val': 'Val'}


class DMLWriter:
    def __init__(self, fd, indent=0, closing_symbol='}'):
        self.fd = fd
        self.indent = indent
        self.closing_symbol = closing_symbol

    def __enter__(self):
        self.indent += 4
        return self

    def __exit__(self, *exc):
        self.indent -= 4
        self.write(self.closing_symbol)
        return False

    def write(self, data):
        self.fd.write(f'{"":>{self.indent}}{data}'.rstrip() + "\n")


def manual_register(name):
    rnsam_regs = ['non_hash_mem_region',
                  'non_hash_tgt_nodeid',
                  'sys_cache_group_hn_count',
                  'sys_cache_grp_hn_nodeid',
                  'sys_cache_grp_region',
                  'sys_cache_grp_secondary_reg',
                  ]
    hnf_regs = ['sam_memregion', 'slc_lock_base']

    hni_regs = ['sam_addrregion']

    for r in rnsam_regs + hnf_regs + hni_regs:
        if r in name:
            return True
    return False


def getText(o, attr):
    return o.find(f'.//{{*}}{attr}').text


def getInt(o, attr):
    txt = getText(o, attr).replace(
        "'h", "0x").replace("/", "//").replace("$", "")
    return eval(txt)  # unsafe, but we trust the input


def getSize(o):
    return getInt(o, 'size') // 8


def getNode(o):
    return getText(o, 'name').split('_u_')[-1]


def getName(o):
    return getText(o, 'name').split('_u_')[0]


def getNid(o):
    for field in ['node_id', 'xy_id']:
        if o.find(f".//{{*}}field[{{*}}name='{field}']") is not None:
            return getReset(o, field)
    return None


def getType(o):
    return getReset(o, 'node_type')


def getAddr(o):
    return getInt(o, 'addressOffset')


def getDesc(o):
    return getText(o, 'description')


def getResetSpirit(o, field=None):
    reset = int(o.find('./{*}reset/{*}value').text, 0)
    if field:
        fld = o.find(f".//{{*}}field[{{*}}name='{field}']")
        lsb = getInt(fld, 'bitOffset')
        msk = int("1" * getInt(fld, 'bitWidth'), 2)
        return (reset >> lsb) & msk
    else:
        return reset


def getReset(o, field=None):
    if o.find('./{*}reset') is not None:
        # spirit-style: reset value for entire register
        return getResetSpirit(o, field)

    # ipxact-style: reset value for each field
    if field:
        reset = o.find(
            f".//{{*}}field[{{*}}name='{field}']//{{*}}reset")
        return getInt(reset, 'value') & getInt(reset, 'mask')

    val = 0
    for f in o.findall(".//{*}field"):
        val |= getReset(o, getName(f)) << getInt(f, 'bitOffset')
    return val


def getAccess(o):
    return getText(o, 'access').replace('-', '_')


def getFieldRange(o):
    lsb = getInt(o, 'bitOffset')
    msb = lsb + getInt(o, 'bitWidth') - 1
    return (lsb, msb)


def explicit_register(name):
    '''If a register with the given name should be included in glue,
    then return a set of fields to also be included in the
    glue. Otherwise return None.'''
    # Note: in this dict, the value None is a placeholder for manual
    # registers -- those fields don't matter but will matter as soon as
    # manual regs vanish.
    regs = {"cfg_ctl": {'hns_ocm_en', 'hns_ocm_allways_en'},
            "gic_mem_region_reg": {
                'gic_region_base_addr', 'gic_region_size',
                'gic_region_target_type', 'gic_region_valid',
                'gic_region_nodeid'},
            "node_info": set(),
            "non_hash_mem_region": None,
            "non_hash_tgt_nodeid": None,
            "region_cmp_addr_mask_reg": set(),
            "rnsam_status": {'default_target_type', 'default_nodeid',
                             'nstall_req', 'use_default_node'},
            "sam_addrregion_cfg": None,
            "sam_memregion": None,
            "sam_control": {f'hn_cfg_sn{i}_nodeid' for i in range(3)},
            "sam_6sn_nodeid": {f'hn_cfg_sn{i}_nodeid' for i in range(3, 6)},
            "secure_register_groups_override": set(),
            "slc_lock_base": None,
            "slc_lock_ways": {'ways'},
            "sys_cache_group_hn_count": None,
            "sys_cache_grp_cal_mode_reg": set(),
            "sys_cache_grp_hn_nodeid": None,
            "sys_cache_grp_nonhash_nodeid": set(),
            "sys_cache_grp_region": None,
            "sys_cache_grp_secondary": None,
            "unit_info": {'slc_size', 'slc_num_ways', 'nonhash_rcomp_lsb',
                          'nonhash_range_comp_en'},
            }
    for n in regs:
        if n in name:
            fields = regs[n]
            assert fields is not None
            return fields
    return None

def write_regimpl(r, dml):
    fields = [f for f in r.findall('.//{*}field')
              if not getName(f).startswith('reserved_')]
    field_access_types = {getAccess(fld) for fld in fields}
    if len(field_access_types) == 1:
        reg_access = f' is {field_access_types.pop()}'
    else:
        reg_access = ''
    reg_name = getName(r)
    dml.write(f'register {reg_name}{reg_access} {{')
    with dml:
        if 'node_info' in reg_name:
            dml.write('is node_info;')
        dml.write(f'param init_val = 0x{getReset(r):x};')
        for fld in fields:
            lsb, msb = getFieldRange(fld)
            access = f" is {getAccess(fld)}" if not reg_access else ""
            name = getName(fld)
            name = reserved_names.get(name, name)
            dml.write(f'field {name} @ [{msb}:{lsb}]{access};')


def write_regdef(r, dml):
    size = "" if getSize(r) == 8 else f" size {getSize(r)}"
    dml.write(
        f'register {getName(r)}{size} @ 0x{getAddr(r):x} "{getDesc(r)}";')


def write_simple(r, dml):
    fields = [f for f in r.findall('.//{*}field')
              if not getName(f).startswith('reserved_')]
    write_mask = 0
    for fld in fields:
        if (getAccess(fld) != "read_only"):
            bw = getInt(fld, 'bitWidth')
            bo = getInt(fld, 'bitOffset')
            write_mask |= ((1 << bw) - 1) << bo
    dml.write('{0x%x, 0x%x, 0x%x, 0x%x},'
              % (getAddr(r), getSize(r), getReset(r), write_mask))


def write_templates(regs, dml):
    templates = {
        0x4: "hni",    # i/o home node
        0x5: "hnf",    # fully coherent home node
        0xf: "rnsam",  # source address mapping within a requesting node
        0x11: "hni",   # i/o home node with PCIe optimizations
    }
    for r in regs:
        if getName(r).endswith('node_info'):
            node_type = getType(r)
            node_template = templates.get(node_type)
            if node_template:
                dml.write(f'is {node_template};')
                dml.write(f'param {node_template}_offs = 0x{getAddr(r):x};')


def write_bank_params(n, regs, dml):
    for r in regs:
        if getName(r) == 'por_apb_only_access':
            dml.write(f'param apb_only_access = {n}.{getName(r)};')


def write_node(n, regs, dml):
    write_bank_params(n, regs, dml)
    dml.write(f'group {n} is node {{')
    with dml:
        dml.write(f'param node_id = {getNid(regs[0])};')
        dml.write(f'param node_type = {getType(regs[0])};')
        write_templates(regs, dml)

        regs = [r for r in regs if not manual_register(getName(r))]

        for r in regs:
            write_regdef(r, dml)
        dml.write('')

        for r in regs:
            write_regimpl(r, dml)


def write_bank(b, dml, name, simple):
    registers = b.findall('.//{*}register')
    registers.sort(key=lambda x: getInt(x, 'addressOffset'))

    nodes = {}
    if simple:
        simple_regs = []
        for r in registers:
            if explicit_register(getName(r)):
                nodes.setdefault(getNode(r), []).append(r)
            else:
                simple_regs.append(r)
    else:
        for r in registers:
            nodes.setdefault(getNode(r), []).append(r)

    dml.write(f'bank {name}' + ' {')
    with dml:
        dml.write('param register_size = 8;')
        for (n, regs) in nodes.items():
            write_node(n, regs, dml)

        if simple:
            dml.write(f'param simple_regs_len = {len(simple_regs)};')
            dml.write(
                'session simple_register_t simple_regs_info[simple_regs_len] = {')
            with DMLWriter(dml.fd, dml.indent, '};') as sdml:
                for r in simple_regs:
                    write_simple(r, sdml)

def reg_data(bank_anchor, r):
    reg_anchor = f'{bank_anchor}.{getName(r)}'
    fields = {
        f'{reg_anchor}.{getName(f)}':
        dict(name=getName(f),
             lsb=getInt(f, 'bitOffset'),
             bitsize=getInt(f, 'bitWidth'),
             desc=getDesc(f),
             read_only=getAccess(f) == 'read_only',
             reg=reg_anchor)
        for f in r.findall('.//{*}field')
        if not getName(f).startswith('reserved_')}
    reg = dict(name=getName(r),
               offset=getAddr(r),
               size=getSize(r),
               desc=getDesc(r),
               init_val=getReset(r),
               read_only=all(f.read_only for f in fields.values()),
               fields=sorted(fields, key=lambda anchor: fields[anchor].lsb))
    return ((reg_anchor, reg), fields.items())

@dataclass
class FromXML(GlueConfig):
    '''An entity extracted from XML to be included in the data-driven
    model, and possibly included in glue code.

    Note that this dual purpose datastructure only makes sense in a
    CMN-like setting where the glue subset is filtered
    programmatically; with a manually declared glue mapping, the
    structure imposed by GlueConfig can be dropped. For instance,
    `Reg.sub` could be named `fields`.
    '''
    anchor: Union[str, list, None]
    _: dataclasses.KW_ONLY
    object_type: str
    entity_type: Optional[str]
    dims: list[(str, int)] = dataclasses.field(default_factory=list)
    num_local_dims: int = 0
    sub: dict[str, "GlueConfig"]

@dataclass
class Field(FromXML):
    _: dataclasses.KW_ONLY
    object_type: str = 'field'
    entity_type: str = 'field'
    sub: dict[str] = dataclasses.field(default_factory=dict)
    name: str
    desc: str
    lsb: int
    bitsize: int
    read_only: bool

    def data(self, parent):
        return (self.anchor, dict(
            reg=parent.anchor,
            name=reserved_names.get(self.name, self.name),
            lsb=self.lsb,
            bitsize=self.bitsize,
            desc=self.desc,
            read_only=self.read_only,
            lock_ref=[],
            lock_value=0))

@dataclass
class Reg(FromXML):
    _: dataclasses.KW_ONLY
    object_type: str = 'register'
    entity_type: str = 'reg'
    name: str
    offset: int
    size: int
    desc: str
    init_val: int
    sub: dict[str, Field]

    def data(self, parent):
        field_bits = (
            sum(((1 << f.bitsize) - 1) << f.lsb
                for f in self.sub.values())
            if self.sub else (1 << self.size * 8) - 1)

        return (self.anchor, dict(
            bank=parent.bank,
            name=f'{parent.name}.{self.name}',
            offset=self.offset,
            size=self.size,
            desc=self.desc,
            field_bits=field_bits,
            init_val=self.init_val,
            read_only=False,
            fields=[f.anchor for f in self.sub.values()]))

@dataclass
class Node(FromXML):
    _: dataclasses.KW_ONLY
    anchor: str = None
    object_type: str = 'group'
    entity_type: None = None
    name: str
    bank: str
    # (id, type, addr)
    node_infos: list[(Reg, int, int)]
    sub: dict[str, Reg]

def decode_reg(bank_anchor, r):
    reg_anchor = f'{bank_anchor}.{getText(r, "name")}'
    fields = {
        getName(f): Field(
            anchor=f'{reg_anchor}.{getName(f)}',
            name=getName(f),
            desc=getDesc(f),
            lsb=getInt(f, 'bitOffset'),
            bitsize=getInt(f, 'bitWidth'),
            read_only=getAccess(f) == 'read_only')
        for f in r.findall('.//{*}field')
        if not getName(f).startswith('reserved_')}
    reg = Reg(anchor=reg_anchor,
              name=getName(r),
              offset=getAddr(r),
              size=getSize(r),
              desc=getDesc(r),
              init_val=getReset(r),
              sub=fields)
    return (reg, fields)

def decode_node(bank_name:str, node_name: str, regs: list[Reg]):
    # TODO: this is weird: Sven's old code accepted that one node has
    # two node_info regs, as long as at most one reg has a type that
    # requires a template (rnsam, hni, hnf), and this does happen in
    # the cmn700 xml, for the node hnd_nid294. Unsure if this is
    # correct, but trying to keep it bug compatible.
    node_infos = []
    for node_info_reg in regs:
        if node_info_reg.name.endswith('node_info'):
            [f] = [f for (name, f) in node_info_reg.sub.items()
                   if name in ['node_id', 'xy_id']]
            node_id = (node_info_reg.init_val >> f.lsb) & ((1 << f.bitsize) - 1)
            [f] = [f for (name, f) in node_info_reg.sub.items()
                   if name == 'node_type']
            node_type = ((node_info_reg.init_val >> f.lsb)
                         & ((1 << f.bitsize) - 1))
            node_infos.append((node_info_reg, node_id, node_type))
    assert node_infos
    return Node(bank=bank_name, name=node_name, node_infos=node_infos, sub={
        r.anchor: r for r in regs})

def decode_bank(bank_name, bank_xml):
    node_regs = {}
    for r in sorted(bank_xml.findall('.//{*}register'),
                    key=lambda x: getInt(x, 'addressOffset')):
        (reg, reg_fields) = decode_reg(bank_name, r)
        node_regs.setdefault(getNode(r), []).append(reg)
    return [decode_node(bank_name, node_name, regs)
            for (node_name, regs) in node_regs.items()]

def bank_data(bank_name, nodes: list[Node],
              generate_glue: Callable[str, bool]=lambda _: True):
    data = dict(
        bank={bank_name: dict(
                regs=[r.anchor
                      for r in sorted(
                              (r for n in nodes for r in n.sub.values()),
                              key=lambda r: r.offset)])},
        reg=dict(r.data(n) for n in nodes for r in n.sub.values()),
        field=dict(f.data(r)
                   for n in nodes for r in n.sub.values()
                   for f in r.sub.values()))

    glue_config = GlueConfig('device', None, [], 0, None, {
        bank_name: GlueConfig('bank', 'bank', [], 0, bank_name, sub={
            n.name: dataclasses.replace(n, sub={
                r.name: dataclasses.replace(r, sub={
                    f.name: f for f in r.sub.values()
                    if f.name in included_fields})
                for r in n.sub.values()
                # fisketur[syntax-error]
                if (included_fields := generate_glue(r.name)) is not None})
            for n in nodes})})

    return (data, glue_config)

def reg_count(registers, name, s):
    return max(int(getName(r).split(s)[-1])
               for r in registers if name in getName(r)) + 1


def write_params(b, dml):
    # We need to figure out how many hashed targets are supported
    if b.find(".//{*}field[{*}name='nodeid_63']") is not None:
        scg_targets = 64
    else:
        scg_targets = 32

    registers = b.findall('.//{*}register')
    registers.sort(key=lambda x: getInt(x, 'addressOffset'))
    hnd_regs = [r for r in registers if getNode(r).startswith('hnd')]
    hnd_nid = getNid(hnd_regs[0])
    rootnodebase = getInt(hnd_regs[0], 'addressOffset')

    por_info_global = [
        r for r in registers if 'por_info_global' in getName(r)][0]
    address_width = getReset(por_info_global, 'physical_address_width')

    rnsam_unit_info = [
        r for r in registers if 'rnsam_unit_info' in getName(r)][0]
    non_hash_mem = getReset(rnsam_unit_info, 'num_non_hash_group')
    sys_cache_grp = getReset(rnsam_unit_info, 'num_sys_cache_group')
    non_hash_tgt = reg_count(registers, 'non_hash_tgt_nodeid', 'nodeid')
    sys_cache_grp_hn = reg_count(registers, 'sys_cache_grp_hn', 'reg')

    dml.write(f'param ADDRESS_WIDTH default {address_width};')
    dml.write(f'param HND_NID default {hnd_nid};')
    dml.write(f'param ROOTNODEBASE default 0x{rootnodebase:x};')
    dml.write(f'param NUM_SCG_TARGETS default {scg_targets};')
    dml.write(f'param NUM_NON_HASH_MEM default {non_hash_mem};')
    dml.write(f'param NUM_NON_HASH_TGT default {non_hash_tgt};')
    dml.write(f'param NUM_SYS_CACHE_GRP default {sys_cache_grp};')
    dml.write(f'param NUM_SYS_CACHE_GRP_HN default {sys_cache_grp_hn};')
    dml.write('')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='parse register xml and generate DML')

    parser.add_argument('src', help="source xml files", nargs='+')
    parser.add_argument('glue_dst', type=Path, help="destination dml file")
    parser.add_argument(
        'resource', type=str,
        help="Name of resource file, relative to the simmod package")
    parser.add_argument('--bank', action="append",
                        help="name of address block to parse")
    parser.add_argument('--apb-bank', help="name of APB address block to parse")
    parser.add_argument('--hns-work-around', action='store_true',
                        help=("Rewrite the reset value of cmn_hns_unit_info "
                              + "registers to reflect 1 MB SLC over 16 ways"))
    parser.add_argument('--test-lock', action='store_true',
                        help='add some dummy regs to test lock templates')
    args = parser.parse_args()

    bank = etree.Element('bank')
    apb_bank = etree.Element('apb_bank')
    for f in args.src:
        root = etree.parse(f).getroot()
        for ab in root.findall('.//{*}addressBlock'):
            if getName(ab) in args.bank:
                for r in ab.findall('.//{*}register'):
                    bank.append(r)
            if getName(ab) == args.apb_bank:
                for r in ab.findall('.//{*}register'):
                    apb_bank.append(r)

    regs_nodes = decode_bank('regs', bank)


    # test-cmn-700 does an extremely ad-hoc workaround to rewrite the
    # init_val of cmn_hns_unit_info:s, as they apparently always inaccurately
    # reflect zero-sized SLC. The workaround rewrites them to always reflect
    # 1 MB SLC over 16 ways
    # thanks Sven i spent like 4-5 hours debugging this
    if args.hns_work_around:
        for r in (r for n in regs_nodes for r in n.sub.values()
                  if r.name == 'cmn_hns_unit_info'):
            # Sets slc_size to 0b100, and slc_num_ways to 16
            r.init_val = r.init_val | 0x1004

    (data, glue_config) = bank_data(
        'regs', regs_nodes,
        lambda name: None if manual_register(name) else explicit_register(name))

    if args.test_lock:
        regs = glue_config.sub['regs']
        regs.sub['locked'] = Reg(
            object_type='register', entity_type='reg', dims=[],
            anchor=None, name='locked', offset=1000000000,
            size=8, desc='foo', init_val=0,
            sub={'f3': Field(
                object_type='field', entity_type='field', dims=[],
                anchor='regs.locked.f3', sub={}, name='f3',
                desc='f3', lsb=32, bitsize=16, read_only=False)})
        data['field'].update({
            'regs.por_mxp_node_info_u_smxp_0_0.node_type': {
                'reg': 'regs.por_mxp_node_info_u_smxp_0_0',
                'name': 'node_type', 'lsb': 0, 'bitsize': 16,
                'desc': 'CMN-600 node type identifier',
                'read_only': True, 'lock_ref': [], 'lock_value': 0},
            'regs.locked.f1': dict(
                reg='regs.locked', name='f1', lsb=0, bitsize=16,
                desc='locked field', read_only=False,
                lock_ref=['regs.locked.f2'], lock_value=1),
            'regs.locked.f2': dict(
                reg='regs.locked', name='f2', lsb=16, bitsize=16,
                desc='lock field', read_only=False, lock_ref=[], lock_value=0),
            'regs.locked.f3': dict(
                reg='regs.locked', name='f3', lsb=32, bitsize=16,
                desc='locked field', read_only=False,
                lock_ref=['regs.locked.f2'], lock_value=2)})
        data['reg']['regs.locked'] = dict(
                bank='regs', name='locked', offset=1000000000,
                size=8, desc='lock 1',
                field_bits=0xffffffffffff, init_val=0,
                read_only=False, fields=[
                    'regs.locked.f1', 'regs.locked.f2', 'regs.locked.f3'])
        data['bank']['regs']['regs'].append('regs.locked')

    dml_body = process_glue_and_data(
        args.resource, 'cmn', dm, glue_config, data)

    with open(args.glue_dst, 'w') as fd:
        fd.write(dml_body)
        dml = DMLWriter(fd)
        dml.write(f'bank regs {{')
        with dml:
            dml.write('param register_size = 8;')
            for n in regs_nodes:
                dml.write(f'group {n.name} is node {{')
                with dml:
                    (_, first_node_id, first_node_type) = n.node_infos[0]
                    dml.write(f'param node_id = {first_node_id};')
                    dml.write(f'param node_type = {first_node_type};')
                    for (node_info_reg, _, node_type) in n.node_infos:
                        node_template = {
                            # i/o home node
                            0x4: "hni",
                            # fully coherent home node
                            0x5: "hnf",
                            # source address mapping within a
                            # requesting node
                            0xf: "rnsam",
                            # i/o home node with PCIe optimizations
                            0x11: "hni",
                        }.get(node_type)
                        if node_template is not None:
                            dml.write(f'is {node_template};')
                            dml.write(f'param {node_template}_offs'
                                      f' = 0x{node_info_reg.offset:x};')

                        dml.write(f'register {node_info_reg.name} '
                                  + 'is node_info;')

        write_params(bank, dml)
        write_bank(apb_bank, dml, 'apb_regs', False)

    # Create a python-list of all registers, used by test s-register-access.py
    registers = bank.findall('.//{*}register')
    registers.sort(key=lambda x: getInt(x, 'addressOffset'))
    with open('regs.py', 'w') as f:
        f.write('regs = [\n')
        f.write('#(address, size, writable, name, description, fields)\n')
        for r in registers:
            addr = getAddr(r)
            size = getSize(r)
            acc = getAccess(r)
            name = getText(r, 'name')
            desc = getDesc(r)
            fields = [(getText(f, 'name'), getFieldRange(f))
                      for f in r.findall('.//{*}field')
                      if not getName(f).startswith('reserved_')]
            f.write(f' {(addr, size, acc, name, desc, fields)},\n')
        f.write(']\n')
