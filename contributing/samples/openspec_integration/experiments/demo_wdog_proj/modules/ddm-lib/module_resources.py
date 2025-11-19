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
from importlib import import_module

# Workaround for python wrapping bugs:
# https://github.com/intel-innersource/applications.simulators.simics.simics-base/pull/7674
# https://github.com/intel-innersource/applications.simulators.simics.simics-base/pull/7676
def path(pypkg, resource_name):
    pkg = import_module(pypkg)
    return os.path.join(pkg.__path__[0], resource_name)
