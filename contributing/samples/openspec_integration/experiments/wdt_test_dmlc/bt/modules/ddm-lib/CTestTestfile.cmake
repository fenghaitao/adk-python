# CMake generated Testfile for 
# Source directory: /home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib
# Build directory: /home/coder/ai_agents/tests/wdt_test_dmlc/bt/modules/ddm-lib
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test([=[modules::test_data_model.py]=] "pytest" "test_data_model.py")
set_tests_properties([=[modules::test_data_model.py]=] PROPERTIES  DEF_SOURCE_LINE "/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/test_data_model.py:1" ENVIRONMENT "SIMICS_BASE=/home/coder/.simics-mcp-server/simics-install/simics-7.57.0" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/coder/ai_agents/tests/wdt_test_dmlc/bt/modules/ddm-lib/sandbox" WORKING_DIRECTORY "/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib" _BACKTRACE_TRIPLES "/home/coder/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1429;add_test;/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/CMakeLists.txt;19;simics_add_test;/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/CMakeLists.txt;0;")
add_test([=[modules::glue_config.py]=] "pytest" "glue_config.py")
set_tests_properties([=[modules::glue_config.py]=] PROPERTIES  DEF_SOURCE_LINE "/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/glue_config.py:1" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/coder/ai_agents/tests/wdt_test_dmlc/bt/modules/ddm-lib/sandbox" WORKING_DIRECTORY "/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib" _BACKTRACE_TRIPLES "/home/coder/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1429;add_test;/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/CMakeLists.txt;20;simics_add_test;/home/coder/ai_agents/tests/wdt_test_dmlc/modules/ddm-lib/CMakeLists.txt;0;")
