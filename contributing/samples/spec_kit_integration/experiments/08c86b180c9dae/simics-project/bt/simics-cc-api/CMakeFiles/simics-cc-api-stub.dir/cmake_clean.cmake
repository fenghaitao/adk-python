file(REMOVE_RECURSE
  "libsimics-cc-api-stub.a"
  "libsimics-cc-api-stub.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/simics-cc-api-stub.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
