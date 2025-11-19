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

simics_add_module(ddm-lib
  SOURCES module_resources.py
  SIMICS_API 6
)

# our windows env does not yet have a pytest venv
if(NOT WIN32)
  simics_add_test(test_data_model.py PYTEST ENV SIMICS_BASE=${SIMICS_BASE_DIR})
  simics_add_test(glue_config.py PYTEST)
endif()
