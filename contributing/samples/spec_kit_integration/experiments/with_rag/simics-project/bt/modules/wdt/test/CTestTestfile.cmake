# CMake generated Testfile for 
# Source directory: /home/hfeng1/demo/rag/simics-project/modules/wdt/test
# Build directory: /home/hfeng1/demo/rag/simics-project/bt/modules/wdt/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test([=[wdt::wdt]=] "/home/hfeng1/demo/rag/simics-project/simics" "--batch-mode" "s-wdt.py")
set_tests_properties([=[wdt::wdt]=] PROPERTIES  DEF_SOURCE_LINE "/home/hfeng1/demo/rag/simics-project/modules/wdt/test/s-wdt.py:1" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/hfeng1/demo/rag/simics-project/bt/modules/wdt/test/sandbox" WORKING_DIRECTORY "/home/hfeng1/demo/rag/simics-project/modules/wdt/test" _BACKTRACE_TRIPLES "/home/hfeng1/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1441;add_test;/home/hfeng1/demo/rag/simics-project/modules/wdt/test/CMakeLists.txt;4;simics_add_test;/home/hfeng1/demo/rag/simics-project/modules/wdt/test/CMakeLists.txt;0;")
add_test([=[wdt::info-status]=] "/home/hfeng1/demo/rag/simics-project/simics" "--batch-mode" "s-info-status.py")
set_tests_properties([=[wdt::info-status]=] PROPERTIES  DEF_SOURCE_LINE "/home/hfeng1/demo/rag/simics-project/modules/wdt/test/s-info-status.py:1" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/hfeng1/demo/rag/simics-project/bt/modules/wdt/test/sandbox" WORKING_DIRECTORY "/home/hfeng1/demo/rag/simics-project/modules/wdt/test" _BACKTRACE_TRIPLES "/home/hfeng1/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1441;add_test;/home/hfeng1/demo/rag/simics-project/modules/wdt/test/CMakeLists.txt;5;simics_add_test;/home/hfeng1/demo/rag/simics-project/modules/wdt/test/CMakeLists.txt;0;")
