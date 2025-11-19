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

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'ddm-lib'))
from ddm_lib import DataModel, Member, EntitySpec, uint8, String, Bool, uint64, Ref, List

dm = DataModel([
    EntitySpec(
        'bank', members=(Member('regs', List(Ref('reg'))),)),
    EntitySpec(
        'reg',
        members=(
            Member('bank', Ref('bank')),
            Member('group', List(Ref('reg_group'), sz_type=uint8())),
            Member('offset', uint64()),
            Member('init_val', uint64()),
            Member('field_bits', uint64()),
            Member('read_only', Bool()),
            Member('name', String()),
            Member('fields', List(Ref('field'), sz_type=uint8())),
            Member('size', uint8()),
            Member('desc', String()),
        )
    ),
    EntitySpec(
        'field',
        members=(
            Member('reg', Ref('reg')),
            Member('group', List(Ref('field_group'), sz_type=uint8())),
            Member('lsb', uint8()),
            Member('bitsize', uint8()),
            Member('read_only', Bool()),
            Member('name', String()),
            Member('desc', String()),
        ),
    ),
    EntitySpec(
        'field_group',
        members=(
            Member('name', String()),
        ),
    ),
    EntitySpec(
        'reg_group',
        members=(
            Member('name', String()),
        ),
    ),
    EntitySpec(
        'handles',
        members=(
            Member('bank', List(Ref('bank'))),
            Member('reg', List(Ref('reg'))),
            Member('field', List(Ref('field'))),
            Member('field_group', List(Ref('field_group'))),
        ),
    ),
])

if __name__ == '__main__':
    test_model_dml = sys.argv[1]
    dm.generate_dmlfile(test_model_dml, 'ipxact_dia')
