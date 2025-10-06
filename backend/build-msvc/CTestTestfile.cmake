# CMake generated Testfile for 
# Source directory: C:/Users/unixthat/coding/ENTROPYMAX2.0/backend
# Build directory: C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/build-msvc
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test(backend_tests "C:/Users/unixthat/coding/ENTROPYMAX2.0/build/bin/test_backend.exe")
  set_tests_properties(backend_tests PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;156;add_test;C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test(backend_tests "C:/Users/unixthat/coding/ENTROPYMAX2.0/build/bin/test_backend.exe")
  set_tests_properties(backend_tests PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;156;add_test;C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test(backend_tests "C:/Users/unixthat/coding/ENTROPYMAX2.0/build/bin/test_backend.exe")
  set_tests_properties(backend_tests PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;156;add_test;C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test(backend_tests "C:/Users/unixthat/coding/ENTROPYMAX2.0/build/bin/test_backend.exe")
  set_tests_properties(backend_tests PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;156;add_test;C:/Users/unixthat/coding/ENTROPYMAX2.0/backend/CMakeLists.txt;0;")
else()
  add_test(backend_tests NOT_AVAILABLE)
endif()
