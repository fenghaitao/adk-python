# © 2023 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

function(cmn_add_tests class module)
  set(cwd ${CMAKE_CURRENT_FUNCTION_LIST_DIR})
  file(GLOB tests CONFIGURE_DEPENDS "${cwd}/s-*.py")
  foreach(test ${tests})
    set(env "CMN_CLASS=${class};CMN_MODULE=${module}")
    simics_add_test(${test} CWD ${cwd} ENV ${env})
  endforeach()
endfunction()

