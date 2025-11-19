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


# import os
# import sys
import yaml
import argparse
from pathlib import Path
from dataclasses import dataclass
import dataclasses

from model_spec import dm

from ddm_lib import process_glue_and_data, GlueConfig

@dataclass
class Entity:
    kind: str
    name: str
    props: dict[str, object] = dataclasses.field(default_factory=dict)
    sub: list('Entity') = dataclasses.field(default_factory=list)


prop_defaults = {
    'bank': {'regs': []},
    'reg': {'group': [], 'init_val': 0, 'read_only': False, 'desc': 'a reg',
            'fields': []},
    'field': {'group': [], 'desc': 'a field'}
}

ddm = [
    Entity('bank', 'b', sub=[
        Entity('reg_group', 'g', sub=[
            Entity('reg', f'r{i}', props={'offset': 0x100 + i*8,
                                          'size': 8,
                                          'init_val': (1 << 64) - 1}, sub=[
                Entity('field_group', 'hi', sub=[
                    Entity('field', f'f{j}', props={'bitsize': 10,
                                                    'lsb': 16*j + 2})
                    for j in range(2,4)
                ]),
                Entity('field_group', 'lo', sub=[
                    Entity('field', f'f{j}', props={'bitsize': 10,
                                                    'lsb': 16*j + 2})
                    for j in range(0,2)
                ]),
            ])
            for i in range(0,6)
        ]),
    ]),
    Entity('bank', 'b_overlap', sub=[
        Entity('reg', 'r0', props={'offset': 0x0, 'size': 8}),
        Entity('reg', 'r1', props={'offset': 0x4, 'size': 8}),
    ]),
]

# OH GOD MY KINGDOM FOR LENSES
def update_purely(a, b):
    a = dict(a)
    for (k, v) in b.items():
        if isinstance(v, dict):
            a[k] = update_purely(a.get(k, {}), v)
        else:
            a[k] = v
    return a

def process_entity(ddm, data, anchor_prefix="", extra_props={}):
    props = ddm.props | extra_props.get(ddm.kind, {})
    anchor = f"{anchor_prefix}{ddm.name}"
    anchor_prefix = anchor + '.'
    props['name'] = ddm.name
    subdata = {}
    if ddm.kind == 'bank':
        sub_extra_props = update_purely(extra_props, {'reg': {'bank': anchor}})
        for sub in ddm.sub:
            process_entity(sub, subdata, anchor_prefix, sub_extra_props)
        props['regs'] = sorted(subdata['reg'],
                               key=lambda k: subdata['reg'][k]['offset'])
    elif ddm.kind == 'reg':
        subdata = {}
        sub_extra_props = update_purely(extra_props, {'field': {'reg': anchor}})
        for sub in ddm.sub:
            process_entity(sub, subdata, anchor_prefix, sub_extra_props)
        fields = sorted(subdata.get('field', {}).items(), key=lambda t: t[1]['lsb'])
        field_bits = (
            sum(((1 << f['bitsize']) - 1) << f['lsb'] for (_, f) in fields)
            if fields else (1 << props['size'] * 8) - 1)
        props['fields'] = [k for (k,_) in fields]
        props['field_bits'] = field_bits
    elif ddm.kind == 'field':
        assert ddm.sub == []
    elif ddm.kind == 'reg_group':
        sub_extra_props = update_purely(extra_props,
                                        {'reg': {'group': [anchor]}})
        for sub in ddm.sub:
            process_entity(sub, data, anchor_prefix, sub_extra_props)
    elif ddm.kind == 'field_group':
        sub_extra_props = update_purely(extra_props,
                                        {'field': {'group': [anchor]}})
        for sub in ddm.sub:
            process_entity(sub, data, anchor_prefix, sub_extra_props)
    else:
        raise Exception('bad entity kind')

    for (k, v) in subdata.items():
        data.setdefault(k, {}).update(v)

    props = prop_defaults.get(ddm.kind, {}) | props
    data.setdefault(ddm.kind, {})[anchor] = props

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('glue_config', type=Path)
    parser.add_argument('--glue-dst', type=Path)
    parser.add_argument('--resource-name', type=str)
    args = parser.parse_args()

    data = {}
    for b in ddm:
        process_entity(b, data)

    glue_config = GlueConfig.from_yaml(args.glue_config)

    dml_body = process_glue_and_data(
        args.resource_name, 'test_dia', dm, glue_config, data)

    with open(args.glue_dst, 'w') as fd:
        fd.write(dml_body)
