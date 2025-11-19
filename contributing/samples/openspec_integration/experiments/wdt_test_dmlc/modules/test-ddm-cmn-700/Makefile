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

all:

MODULE_CLASSES = test-ddm-cmn-700

CMN700_NAME = cmn700_mmg.tar.gz
CMN700_XMLS = cmn700_mmg.xml

# TODO(ah): Referring directly to /nfs/simics/ is problematic, as it puts a
#           hard requirement on the SSC LAB in Stockholm. Outside of this lab
#           the user can set CMN700_TAR variable to avoid this requirement, but
#           the long-term solution would be to put this tarball into
#           build-deps.
ifeq ($(HOST_TYPE),win64)
    CMN700_TAR ?= c:\nfs\simics\dumps\arm\$(CMN700_NAME)
else
    CMN700_TAR ?= $(SIMICS_PROJECT)/artifacts/$(CMN700_NAME)
endif

ifneq ($(TC_CONAN),1)
  ifeq ($(wildcard $(CMN700_TAR)),)
      $(warning Could not access CMN700_TAR at $(CMN700_TAR))
      $(error Failure to locate $(CMN700_NAME))
  endif
endif

$(CMN700_XMLS):
	$(PYTHON) -m tarfile -e $(CMN700_TAR)

GENERATED_GLUE := cmn-registers.dml

SRC_FILES = test-cmn-700.dml
PYTHON_FILES = module_load.py cmn_commands.py regs.py

PYTHON_SRC_FILES = model_spec.py
EXTRA_DIST_SRC_FILES += $(PYTHON_SRC_FILES)

DMLC_FLAGS += -I../ddm-cmn-common
EXTRA_MODULE_VPATH = ddm-lib ddm-cmn-common cmn-common

SIMICS_API := 6
THREAD_SAFE = yes

include $(MODULE_MAKEFILE)

test-cmn-700-dml.c test-cmn-700.dmldep: $(GENERATED_GLUE)

DMLC_FLAGS_USER += --no-compat=shared_logs_on_device

CONFIG := $(SRC_BASE)/$(TARGET)/config.yml
BLOB := instance_ddmdef
$(GENERATED_GLUE): parse-xml.py $(CMN700_XMLS) glued_data_lib.py glue_config.py
	echo "= Generating CMN700 registers ="
	$(PYTHON) $< --bank cmn700_registers --apb-bank APB4_cmn700_registers $(CMN700_XMLS) $@ $(BLOB) --hns-work-around --test-lock

regs.py: $(GENERATED_GLUE);

all: regs.py
