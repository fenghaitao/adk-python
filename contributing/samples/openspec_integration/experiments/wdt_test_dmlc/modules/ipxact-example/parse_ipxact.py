#!/usr/bin/env python

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

"""
Parser for IP-XACT (SPIRIT) XML files to generate DDM specifications.
"""

import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
import dataclasses

from model_spec import dm

sys.path.append(str(Path(__file__).parent.parent / 'ddm-lib'))
from glued_data_lib import process_glue_and_data
from glue_config import GlueConfig

# IP-XACT namespaces - support both SPIRIT 1.5 and IEEE 1685-2022
SPIRIT_NS = {'spirit': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.5'}
IPXACT_NS = {'ipxact': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022'}

# Current namespace to use (will be auto-detected)
NS = None
NS_PREFIX = None


@dataclass
class Entity:
    kind: str
    name: str
    props: dict = dataclasses.field(default_factory=dict)
    sub: list = dataclasses.field(default_factory=list)


def detect_namespace(root):
    """Detect which IP-XACT namespace is used in the XML file."""
    global NS, NS_PREFIX

    # Check for SPIRIT namespace
    if root.find('.//spirit:memoryMap', SPIRIT_NS) is not None:
        NS = SPIRIT_NS
        NS_PREFIX = 'spirit'
        return

    # Check for IPXACT namespace
    if root.find('.//ipxact:memoryMap', IPXACT_NS) is not None:
        NS = IPXACT_NS
        NS_PREFIX = 'ipxact'
        return

    # Default to SPIRIT if not detected
    NS = SPIRIT_NS
    NS_PREFIX = 'spirit'


def get_text(element, tag):
    """Get text from an XML element with namespace."""
    elem = element.find(f'.//{NS_PREFIX}:{tag}', NS)
    return elem.text if elem is not None else None


def get_int(element, tag, default=0):
    """Get integer value from an XML element."""
    text = get_text(element, tag)
    if text is None:
        return default
    # Handle hex values
    text = text.strip()
    if text.startswith('0x') or text.startswith('0X'):
        return int(text, 16)
    return int(text)


def parse_field(field_elem):
    """Parse a field from IP-XACT register."""
    name = get_text(field_elem, 'name')
    desc = get_text(field_elem, 'description') or f'Field {name}'
    lsb = get_int(field_elem, 'bitOffset', 0)
    bitsize = get_int(field_elem, 'bitWidth', 1)

    # Check if field is read-only
    access = get_text(field_elem, 'access')
    read_only = access == 'read-only' if access else False

    return Entity('field', name, props={
        'lsb': lsb,
        'bitsize': bitsize,
        'read_only': read_only,
        'desc': desc,
        'group': []
    })


def parse_register(reg_elem):
    """Parse a register from IP-XACT address block."""
    name = get_text(reg_elem, 'name')
    desc = get_text(reg_elem, 'description') or f'Register {name}'
    offset = get_int(reg_elem, 'addressOffset', 0)
    size = get_int(reg_elem, 'size', 32) // 8  # Convert bits to bytes

    # Get reset value
    reset_elem = reg_elem.find(f'.//{NS_PREFIX}:reset/{NS_PREFIX}:value', NS)
    init_val = 0
    if reset_elem is not None:
        init_text = reset_elem.text.strip()
        if init_text.startswith('0x') or init_text.startswith('0X'):
            init_val = int(init_text, 16)
        else:
            init_val = int(init_text)

    # Check if read-only
    access = get_text(reg_elem, 'access')
    read_only = access == 'read-only' or access == 'write-only' if access else False

    # Parse fields
    fields = []
    for field_elem in reg_elem.findall(f'.//{NS_PREFIX}:field', NS):
        fields.append(parse_field(field_elem))

    return Entity('reg', name, props={
        'offset': offset,
        'size': size,
        'init_val': init_val,
        'read_only': read_only,
        'desc': desc,
        'group': [],
        'fields': fields
    }, sub=fields)


def parse_ipxact(xml_file):
    """Parse IP-XACT XML file and return DDM entity structure."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Detect which namespace is being used
    detect_namespace(root)

    # Find the first memory map and address block
    memory_map = root.find(f'.//{NS_PREFIX}:memoryMap', NS)
    if memory_map is None:
        raise ValueError("No memory map found in IP-XACT file")

    bank_name = get_text(memory_map, 'name') or 'ipxact_bank'

    # Parse all registers from address blocks
    registers = []
    for addr_block in memory_map.findall(f'.//{NS_PREFIX}:addressBlock', NS):
        for reg_elem in addr_block.findall(f'.//{NS_PREFIX}:register', NS):
            registers.append(parse_register(reg_elem))

    # Create bank entity
    bank = Entity('bank', bank_name, props={'regs': registers}, sub=registers)

    return [bank]


def generate_glue_config(banks):
    """Generate glue configuration programmatically from parsed banks."""
    glue_dict = {}

    for bank in banks:
        bank_anchor = bank.name.replace('-', '_')  # Make valid DML identifier
        bank_config = {
            'anchor': bank_anchor
        }

        # Add each register directly as a key in the bank config
        for reg in bank.sub:
            reg_name = reg.name
            reg_config = {
                'anchor': f".{reg_name}"  # Relative to bank
            }

            # Add fields if present
            for field in reg.sub:
                field_name = field.name
                field_config = {
                    'anchor': f".{field_name}"  # Relative to register
                }
                reg_config[f'field {field_name}'] = field_config

            bank_config[f'register {reg_name}'] = reg_config

        glue_dict[f'bank {bank_anchor}'] = bank_config

    return glue_dict


def ipxact_to_data(banks):
    """Convert parsed IP-XACT banks to DDM data format."""
    data = {
        'field_group': {},  # Required by DDM even if empty
        'reg_group': {}     # Required by DDM even if empty
    }

    for bank in banks:
        bank_anchor = bank.name.replace('-', '_')  # Make valid DML identifier
        bank_props = {'regs': []}

        # Process each register
        for reg in bank.sub:
            reg_anchor = f"{bank_anchor}.{reg.name}"

            # Calculate field bits
            field_bits = 0
            reg_props = {
                'bank': bank_anchor,
                'group': [],
                'offset': reg.props['offset'],
                'size': reg.props['size'],
                'init_val': reg.props['init_val'],
                'read_only': reg.props['read_only'],
                'name': reg.name,
                'desc': reg.props['desc'],
                'fields': []
            }

            # Process fields
            for field in reg.sub:
                field_anchor = f"{reg_anchor}.{field.name}"
                field_bits |= ((1 << field.props['bitsize']) - 1) << field.props['lsb']

                field_props = {
                    'reg': reg_anchor,  # Use fully qualified anchor
                    'group': [],
                    'lsb': field.props['lsb'],
                    'bitsize': field.props['bitsize'],
                    'read_only': field.props['read_only'],
                    'name': field.name,
                    'desc': field.props['desc']
                }

                data.setdefault('field', {})[field_anchor] = field_props
                reg_props['fields'].append(field_anchor)

            reg_props['field_bits'] = field_bits
            data.setdefault('reg', {})[reg_anchor] = reg_props
            bank_props['regs'].append(reg_anchor)

        data.setdefault('bank', {})[bank_anchor] = bank_props

    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse IP-XACT XML and generate DDM glue code')
    parser.add_argument('ipxact_file', help='IP-XACT XML file to parse')
    parser.add_argument('glue_output', help='Output glue DML file')
    parser.add_argument('resource_name', help='Resource name for DDM')
    parser.add_argument('--save-config', help='Save intermediate glue config to YAML file',
                        default=None)

    args = parser.parse_args()

    print(f"Parsing IP-XACT file: {args.ipxact_file}")

    # Parse IP-XACT
    banks = parse_ipxact(args.ipxact_file)

    print(f"Parsed {len(banks)} banks:")
    for bank in banks:
        print(f"  Bank '{bank.name}' with {len(bank.sub)} registers")

    # Convert to data format
    data = ipxact_to_data(banks)

    # Generate glue configuration programmatically
    glue_dict = generate_glue_config(banks)

    # Save intermediate config if requested
    if args.save_config:
        import yaml
        config_path = args.save_config
        print(f"Saving intermediate glue config to: {config_path}")
        with open(config_path, 'w') as f:
            yaml.dump(glue_dict, f, default_flow_style=False, sort_keys=False)

    print(f"DEBUG: Glue dict top-level keys: {list(glue_dict.keys())}")
    if glue_dict:
        first_key = list(glue_dict.keys())[0]
        print(f"DEBUG: First bank '{first_key}' has {len(glue_dict[first_key])} items")

    glue_config = GlueConfig.from_yaml_tree(glue_dict)

    print(f"Generating glue DML: {args.glue_output}")

    # Generate glue code
    dml_body = process_glue_and_data(
        args.resource_name, 'ipxact_dia', dm, glue_config, data)

    # Write output
    with open(args.glue_output, 'w') as fd:
        fd.write(dml_body)

    print(f"DDM generation complete!")
    print(f"  Registers: {len(data.get('reg', {}))}")
    print(f"  Fields: {len(data.get('field', {}))}")
