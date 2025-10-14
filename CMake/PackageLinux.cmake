set(CPACK_GENERATOR "DEB")
set(CPACK_PACKAGE_NAME "RhizoVisionExplorer")
set(CPACK_PACKAGE_VERSION "2.0.3")
set(CPACK_PACKAGE_CONTACT "seethepallia@ornl.gov")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "RhizoVisionExplorer is a tool for analyzing root images.")
set(CPACK_PACKAGE_VENDOR "Oak Ridge National Laboratory")
set(CPACK_PACKAGE_LICENSE "GPL 3.0")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "seethepallia@ornl.gov") # required

set(CPACK_DEBIAN_PACKAGE_DEPENDS "libc6 (>= 2.34), libstdc++6 (>= 11), libqt6core6 (>= 6.4.0), libqt6widgets6 (>= 6.4.0), libqt6gui6 (>= 6.4.0), libqt6opengl6 (>= 6.4.0), libqt6charts6 (>= 6.4.0), libopencv-core406t64, libopencv-imgproc406t64, libopencv-highgui406t64, libopencv-videoio406t64")

include(CPack)

