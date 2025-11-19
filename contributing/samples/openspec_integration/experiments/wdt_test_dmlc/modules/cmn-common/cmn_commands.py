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


import cli
from dev_util import Register_LE, Bitfield_LE
from simics import VT_get_attributes, SIM_log_error
from table import *

import re

major_types = [0x4, 0x5, 0x7, 0xa, 0xd]

node_types = {
    "DVM": 0x1,     # Distributed Virtual Memory Node
    "CFG": 0x2,     # Configuration Node
    "DTC": 0x3,     # Debug Trace Control Node
    "HN-I": 0x4,    # I/O Home Node
    "HN-F": 0x5,    # Fully coherent Home Node
    "XP": 0x6,      # Crosspath Node
    "SBSX": 0x7,    # AMBA 5 CHI to ACE5-Lite bridge Node
    "MPAM-S": 0x8,  # Memory Partitioning and Monitoring
    "MPAM-NS": 0x9, # Memory Partitioning and Monitoring
    "RN-I": 0xA,    # I/O coherent Requesting Node
    "RN-D": 0xD,    # I/O coherent Requesting Node with DVM
    "RN-SAM": 0xF,  # Source Address Mapping within a Requesting Node
    "HN-P": 0x11,   # Home Node PCIe Optimization
    "CCRA": 0x103,
    "CCHA": 0x104,
    "CCLA": 0x105,
    "CCLA-RNI": 0x106,
}

node_names = {v: k for (k, v) in node_types.items()}

child_ptr_bf = Bitfield_LE({"external": (31, 31), "offs": (27, 0)})
info_bf = Bitfield_LE({"node_id": (31, 16), "node_type": (15, 0)})
child_bf = Bitfield_LE({"offs": (31, 16), "cnt": (15, 0)})


def register(obj, addr, size=8, *args, **kwargs):
    return Register_LE(
        obj.bank.regs, addr, size=size, *args, **kwargs)


def get_child_nodes(obj, addr):
    """Recursively find all children below the node defined at addr"""
    child_info = register(obj, addr + 0x80, bitfield=child_bf)
    if (child_info.offs == 0):
        return []
    child_ptr_offs = addr + child_info.offs
    return [register(obj, child_ptr_offs + i * 8, bitfield=child_ptr_bf)
            for i in range(child_info.cnt)]


def nid_from_addr(addr):
    ptr = addr >> 14
    nid = (ptr >> 2) & 3
    nid |= (ptr & 1) << 2
    nid |= ((ptr >> 6) & 7) << 3
    nid |= ((ptr >> 9) & 7) << 6
    rnfb = (ptr >> 4) & 3 == 0b11
    return (nid, rnfb)


def find_nodes(obj, node_type=None, offs=None):
    """Recursively find all nodes of a given type"""
    offs = obj.rootnodebase if offs is None else offs
    nfo = register(obj, offs, bitfield=info_bf)
    if nfo.node_type == node_type or node_type is None:
        val = [nfo]
    else:
        val = []
    for ch in get_child_nodes(obj, offs):
        try:
            val += find_nodes(obj, node_type, ch.offs)
        except:
            nid, rnfb = nid_from_addr(ch.offs)
            SIM_log_error(
                obj, 0, "failed to probe node %d (rnfb:%s)" % (nid, rnfb))
    return val


class CmnNode:
    obj = None
    node_type = None
    node_id = None

    def add(self, obj, nfo):
        if self.obj is None:
            self.obj = obj
            self.nfo = nfo
            self.node_id = nfo.node_id
            self.x = nfo.x
            self.y = nfo.y
            self.subtypes = []

        if nfo.node_type in major_types:
            self.node_type = nfo.node_type
        else:
            self.subtypes.append(nfo.node_type)

    def to_string(self, **kwargs):
        data = [
            ["Node ID", self.node_id],
            ["Type", "%-6s" % node_names.get(self.node_type, "")]
        ] + [["", "%-6s" % node_names.get(n, hex(n))] for n in self.subtypes]

        return Table([], data).to_string(no_row_column=True, **kwargs)


def print_grid(obj):
    # The Node ID format depends on the dimension of the grid, which
    # is what we're trying to determine. To figure out if 3 or 2 bits
    # are used we find all crosspath nodes and check if 2 bits would
    # be enough to represent all of their x,y coordinates. If not, we
    # assume 3 bits is used.
    xp_nodes = find_nodes(obj, node_types['XP'])
    xy_ids = [r.node_id >> 3 for r in xp_nodes]
    bitsize = 3 if any(i & ~0b1111 for i in xy_ids) else 2

    xlen = max(i >> bitsize for i in xy_ids) + 1
    ylen = max(i & ((1 << bitsize) - 1) for i in xy_ids) + 1

    # Monkey-patch the bitfield-ranges
    if xlen > 4 or ylen > 4:
        info_bf.field_ranges['x'] = (22, 25)
        info_bf.field_ranges['y'] = (19, 21)
        info_bf.field_ranges['p'] = (18, 18)
    else:
        info_bf.field_ranges['x'] = (21, 22)
        info_bf.field_ranges['y'] = (19, 20)
        info_bf.field_ranges['p'] = (18, 18)

    # Create a node-dictionary
    nodes = {}
    for nfo in find_nodes(obj):
        if nfo.node_type == node_types['XP']:
            continue  # Cross-Path nodes are boring
        nodes.setdefault(nfo.node_id, CmnNode()).add(obj, nfo)

    # Format the data for Table
    grid = [["%16s" % ((x, y),) for x in range(xlen)] for y in range(ylen)]
    for n in sorted(nodes.values(), key=lambda x: x.node_id, reverse=True):
        grid[n.y][n.x] += '\n' + n.to_string()
    grid.reverse()  # 0,0 is bottom left corner
    print(Table([], grid).to_string(no_row_column=True))

#
# ------------------------ info -----------------------
#


def get_info(obj):
    return []

#
# ------------------------ status -----------------------
#


def get_status(obj):
    msdata = []  # TODO
    return [["Memory Spaces", msdata]]


def add_commands(class_name):
    cli.new_info_command(class_name, get_info)
    cli.new_status_command(class_name, get_status)
    cli.new_command("print-grid", print_grid,
                    cls=class_name,
                    short="print the CMN connectivity grid",
                    doc="""Prints the CMN connectivity grid along with Node
                    ID, type, target device and source memory-space if
                    applicable""")
