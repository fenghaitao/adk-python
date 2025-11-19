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


import argparse
import xml.etree.ElementTree as etree

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
    regs = ["cfg_ctl",
            "gic_mem_region_reg",
            "node_info",
            "non_hash_mem_region",
            "non_hash_tgt_nodeid",
            "region_cmp_addr_mask_reg",
            "rnsam_status",
            "sam_addrregion_cfg",
            "sam_memregion",
            "sam_control",
            "sam_6sn_nodeid",
            "secure_register_groups_override",
            "slc_lock_base",
            "slc_lock_ways",
            "sys_cache_group_hn_count",
            "sys_cache_grp_cal_mode_reg",
            "sys_cache_grp_hn_nodeid",
            "sys_cache_grp_nonhash_nodeid",
            "sys_cache_grp_region",
            "sys_cache_grp_secondary",
            "unit_info",
            ]
    return any(n in name for n in regs)


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

    dml.write(f'bank {name}' + ' is simple_regs' * simple + ' {')
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
    parser.add_argument('dst', help="destination dml file")
    parser.add_argument('--bank', action="append",
                        help="name of address block to parse")
    parser.add_argument('--apb_bank', help="name of APB address block to parse")
    args = parser.parse_args()

    bank = etree.Element('bank')
    apb_bank = etree.Element('apb_bank')
    for f in args.src:
        root = etree.parse(f).getroot()
        for ab in root.findall('.//{*}addressBlock'):
            if not args.bank or getName(ab) in args.bank:
                for r in ab.findall('.//{*}register'):
                    bank.append(r)
            if getName(ab) == args.apb_bank:
                for r in ab.findall('.//{*}register'):
                    apb_bank.append(r)

    with open(args.dst, 'w') as fd:
        dml = DMLWriter(fd)
        dml.write('dml 1.4;')
        write_params(bank, dml)
        write_bank(bank, dml, 'regs', True)
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
