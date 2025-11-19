ddm-cmn-common: ddm-lib
demo_watchdog: ddm-lib
test-ddm-cmn-700: ddm-cmn-common
ipxact-example: ddm-lib
linux64/obj/modules/module-deps.d: modules/ddm-cmn-common/MODULEDEPS modules/demo_watchdog/MODULEDEPS modules/ipxact-example/MODULEDEPS modules/test-ddm-cmn-700/MODULEDEPS
modules/ddm-cmn-common/MODULEDEPS modules/demo_watchdog/MODULEDEPS modules/ipxact-example/MODULEDEPS modules/test-ddm-cmn-700/MODULEDEPS:
ddm-cmn-common ddm-lib:
