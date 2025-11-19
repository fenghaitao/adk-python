<!---
© 2010 Intel Corporation

This software and the related documents are Intel copyrighted materials, and
your use of them is governed by the express license under which they were
provided to you ("License"). Unless the License provides otherwise, you may
not use, modify, copy, publish, distribute, disclose or transmit this software
or the related documents without Intel's prior written permission.

This software and the related documents are provided as is, with no express or
implied warranties, other than those that are expressly stated in the License.
-->

# Coherent Mesh Network shared sources

- `major 6`
- `note 6` First release.
- `note 6` Port to DML 1.4.
- `note 6` Rename to cmn-common
- `release 6 6150`
- `note 6` Register-access test now tests accessing unmapped addresses too.
- `note 6` The reset value of rnsam\_unit\_info is now used to deduce the number of Non Hashed Groups and System Cache Groups, instead of counting register instances.
- `note 6` The parameters generated when parsing the register xml can now be overridden. This can be useful when handling faulty XML sources.
- `note 6` Fixed a bug in SLC size calculation.
- `note 6` An image-based template is used to handle simple Read-Write and Read-Only registers, without side-effects. These registers will not be visible in the register-view of the device. This reduces module size, memory footprint and speeds up compilation time.
- `release 6 6173`
- `note 6` Fixed a bug in OCM region locking.
- `release 6 6174`
- `note 6` Added support for nonhashed groups with *Configurable lower address and upper address*.
- `note 6` Added support for CAL2 and CAL4 in System Cache Groups
- `note 6` The register now bank uses `transaction` instead of `io_memory`.
- `release 6 6175`
- `note 6`  Fix bug when CMN is accessed with transaction larger than 8 bytes. This fix requires Simics-Base version 6.0.143 or later. 
- `release 6 6176`
- `note 6` Objects listed in `sbsx_targets` are now mapped with offset equal to base.
- `note 6` The configuration registers are now available from each requesting node, on the offset defined by the `periphbase` attribute. This can also be driven by the port `CFGM_PERIPHBASE`.
- `release 6 6177`
- `note 6` Added support for the fields `default_nodeid` and `use_default_node` in register `rnsam_status`.
- `note 6` Fixed bug in base-address calculation for CMN-700 regions.
- `release 6 6184`
- `note 6` The data in regs.py, which is generated to help testing, now includes the full name of each register, as well as all fields.
- `release 6 6190`
- `note 6` While in reset, accesses through the RN-I spaces are now forwarded to a dedicated IGNORE port, rather than to the 'regs' bank object.
- `note 6` Fixed bug when accesses are forwarded to the default node, with respect to the `rnsam_status.use_default_node` field.
- `note 6` Use standard `ElementTree` instead of `lxml.etree` when parsing xml.
- `release 6 6191`
- `note 6` Removed workaround for incorrect field names presented in register\_view (fixes SIMICS-18244).
- `release 6 6192`
- `note 6` Fixed a bug on `base_addr` field size for HN-I address regions in CMN-700.
- `release 6 6216`
- `note 6` Added APB registers, apb\_regs and chi\_axi\_regs banks.
- `major 7`
- `release 6 6258`
- `note 6` Fixed a bug where the bitrange of the `addr_region_size` field was incorrect for HN-I address regions in CMN-700.
- `release 6 6285`