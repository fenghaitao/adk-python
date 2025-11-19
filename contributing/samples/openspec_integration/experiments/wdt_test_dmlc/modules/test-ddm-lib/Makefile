# -*- Makefile -*-

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

# Simics module makefile

MODULE_CLASSES = test_ddm_lib

DATA_MODEL := test-ddm-lib-data-model.dml
GENERATED_GLUE := test-ddm-lib-glue.dml

SRC_FILES = test-ddm-lib.dml

PYTHON_SRC_FILES = model_spec.py gen_ddm.py
EXTRA_DIST_SRC_FILES += $(PYTHON_SRC_FILES)

EXTRA_MODULE_VPATH = ddm-lib

SIMICS_API := latest
THREAD_SAFE = yes

include $(MODULE_MAKEFILE)

test-ddm-lib-dml.c test-ddm-lib.dmldep: $(GENERATED_GLUE) $(DATA_MODEL)

DMLC_FLAGS_USER += --no-compat=shared_logs_on_device

$(DATA_MODEL): model_spec.py data_model_lib.py
	$(info Generating $(DATA_MODEL))
	$(PYTHON) $< $@

GLUE_CONFIG := $(SRC_BASE)/$(TARGET)/glue_config.yaml
RESOURCE := instance_ddmdef

$(GENERATED_GLUE): gen_ddm.py glued_data_lib.py glue_config.py $(GLUE_CONFIG)
	$(info Generating DDM)
	$(PYTHON) $< $(GLUE_CONFIG) --glue-dst $@ --resource-name $(RESOURCE)

all: $(GENERATED_GLUE)
