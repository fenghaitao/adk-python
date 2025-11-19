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


from cmn_600_common import create_cmn_600

cmn = create_cmn_600()

simics.SIM_run_command('%s.status' % cmn.name)
simics.SIM_run_command('%s.info' % cmn.name)
simics.SIM_run_command('%s.print-grid' % cmn.name)
