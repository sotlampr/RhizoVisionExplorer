# copy_runtime_deps.cmake
#
# This script is invoked at build time via cmake -P.
# It expects the following variables to be defined:
#   - TARGET_FILE: the full path to the built target (e.g. an .exe or .dll)
#   - INSTALL_BIN: the directory where the target is located (for copying dependencies)
#
# It uses file(GET_RUNTIME_DEPENDENCIES) (available in CMake 3.21+) to determine
# the runtime dependencies of the target and then copies each dependency into the INSTALL_BIN folder.

if(NOT DEFINED TARGET_FILE)
  message(FATAL_ERROR "TARGET_FILE not defined")
endif()

if(NOT DEFINED INSTALL_BIN)
  message(FATAL_ERROR "INSTALL_BIN not defined")
endif()

# Get runtime dependencies for the given target file.
file(GET_RUNTIME_DEPENDENCIES
  LIBRARIES "${TARGET_FILE}"
  EXECUTABLES "${TARGET_FILE}"
  DIRECTORIES ${SEARCH_DIRS}
  RESOLVED_DEPENDENCIES_VAR deps
  UNRESOLVED_DEPENDENCIES_VAR unresolved
)

message(STATUS "Scanning runtime dependencies for: ${TARGET_FILE}")
message(STATUS "Found dependencies:")

foreach(dep IN LISTS deps)
  #message(STATUS "  ${dep}")
  # Extract the file name from the full path.
  if(dep MATCHES "^[cC]:[\\\\/][wW][iI][nN][dD][oO][wW][sS][\\\\/][sS]ystem32")
    #message(STATUS "Skipping system dependency: ${dep}")
  else()
    get_filename_component(dep_name "${dep}" NAME)
    set(dest "${INSTALL_BIN}/${dep_name}")
    if(NOT EXISTS "${dest}")
      file(INSTALL "${dep}" DESTINATION "${INSTALL_BIN}")
      message(STATUS "Copied ${dep} to ${INSTALL_BIN}")
    else()
      message(STATUS "Already exists: ${dest}")
    endif()
  endif()
endforeach()

# # Process unresolved dependencies.
# if(unresolved)
#   message(WARNING "There are unresolved dependencies:")
#   foreach(dep IN LISTS unresolved)
#     message(STATUS "  ${dep}")
#     get_filename_component(dep_name "${dep}" NAME)
#     # If the dependency appears to be a system DLL (using common prefixes), ignore it.
#     string(REGEX MATCH "^(api-ms-win|ext-ms-win|ext-ms-onecore|ext-ms-mf)" _ignore "${dep_name}")
#     if(_ignore)
#       message(STATUS "Ignoring system dependency: ${dep_name}")
#     else()
#       message(WARNING "Unresolved dependency: ${dep}")
#     endif()
#   endforeach()
# endif()
