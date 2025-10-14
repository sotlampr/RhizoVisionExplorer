# Include the CPack module
# include(CPack)

# Set the package na/////me and version
set(CPACK_PACKAGE_NAME "RhizoVisionExplorer")
set(CPACK_PACKAGE_VERSION "2.0.3")

# Set the package maintainer
set(CPACK_PACKAGE_CONTACT "seethepallia@ornl.gov")

# Set the package description
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "RhizoVisionExplorer is a tool for analyzing root images.")

# Set the package vendor
set(CPACK_PACKAGE_VENDOR "Oak Ridge National Laboratory")

# Set the package license
set(CPACK_PACKAGE_LICENSE "GPL 3.0")

# Set the package URL
set(CPACK_PACKAGE_URL "https://www.rhizovision.com/")

# # Set the package file name
# set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-$<CONFIG>-${CPACK_PACKAGE_VERSION}")

# Set the package directory based on the install prefix
set(CPACK_PACKAGE_DIRECTORY "${CMAKE_INSTALL_PREFIX}/packages")

# # Set the package type (e.g., ZIP, TGZ, NSIS, DEB, RPM)
# set(CPACK_GENERATOR "ZIP;TGZ;NSIS;DEB;RPM")

# Exclude specific paths from the source package
set(CPACK_SOURCE_IGNORE_FILES
    "/build/.*"
    "/install/.*"
    "/packages/.*"
    "/.git/.*"
    "/.vscode/.*"
    "/.vs/.*"
    "/x64/.*"
    "/.gitignore"
    "/RhizoVisionExplorer.sln"
)

set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}")

set(CPACK_SOURCE_GENERATOR "ZIP")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CPACK_PACKAGE_VERSION}-source")

message(STATUS "CPack: ${CPACK_PACKAGE_FILE_NAME}")
message(STATUS "CPack package directory: ${CPACK_PACKAGE_DIRECTORY}")
message(STATUS "CMake binary directory: ${CMAKE_BINARY_DIR}")
message(STATUS "CMake source directory: ${CMAKE_SOURCE_DIR}")
message(STATUS "CMake install directory: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "CMake current directory: ${CMAKE_CURRENT_SOURCE_DIR}")

# Include CPack at the end of the CMakeLists.txt file
include(CPack)

# Configure CPack
cpack_add_component_group(RhizoVisionExplorer)
cpack_add_component(RhizoVisionExplorer
    DISPLAY_NAME "RhizoVisionExplorer"
    DESCRIPTION "An application for analyzing plant root images"
    REQUIRED
)

cpack_add_component(rv
    DISPLAY_NAME "rv CLI"
    DESCRIPTION "Command-line interface for RhizoVisionExplorer"
)


