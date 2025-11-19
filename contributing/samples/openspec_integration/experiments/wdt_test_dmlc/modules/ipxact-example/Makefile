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

MODULE_CLASSES = ipxact_example

DATA_MODEL := ipxact-data-model.dml
GENERATED_GLUE := ipxact-example-glue.dml

SRC_FILES = ipxact-example.dml

PYTHON_SRC_FILES = model_spec.py parse_ipxact.py
EXTRA_DIST_SRC_FILES += $(PYTHON_SRC_FILES) wdt_example.xml

EXTRA_MODULE_VPATH = ddm-lib

SIMICS_API := latest
THREAD_SAFE = yes

include $(MODULE_MAKEFILE)

ipxact-example-dml.c ipxact-example.dmldep: $(GENERATED_GLUE) $(DATA_MODEL)

DMLC_FLAGS_USER += --no-compat=shared_logs_on_device

$(DATA_MODEL): model_spec.py data_model_lib.py
	$(info Generating $(DATA_MODEL))
	$(PYTHON) $< $@

RESOURCE := instance_ddmdef

$(GENERATED_GLUE): parse_ipxact.py data_model_lib.py glue_config.py glued_data_lib.py wdt_example.xml
	$(info Generating DDM from IP-XACT)
	$(PYTHON) $< $(word 5,$^) $@ $(RESOURCE) --save-config glue_config_generated.yaml

all: $(GENERATED_GLUE)
