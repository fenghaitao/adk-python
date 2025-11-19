# -*- Makefile -*-

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

# Simics module makefile

default:

EXTRA_DIST_SRC_FILES = parse-xml.py

default: cmn-model.dml

EXTRA_MODULE_VPATH = ddm-lib

SIMICS_API := 6
THREAD_SAFE = yes

include $(MODULE_MAKEFILE)

cmn-model.dml: model_spec.py data_model_lib.py
	$(info Generating cmn-model.dml)
	$(PYTHON) $< $@
