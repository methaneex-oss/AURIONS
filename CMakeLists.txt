cmake_minimum_required(VERSION 3.20)

project(AURIONS
    VERSION 0.1.0
    DESCRIPTION "Adaptive, persistent intelligence system"
    LANGUAGES CXX
)

include(CTest)

option(AURIONS_BUILD_TESTS "Build AURIONS tests" ${BUILD_TESTING})

add_library(aurions_core
    core/cpp/src/version.cpp
)

target_include_directories(aurions_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/include>
)

target_compile_features(aurions_core PUBLIC cxx_std_20)

set_target_properties(aurions_core PROPERTIES
    CXX_EXTENSIONS OFF
)

if(AURIONS_BUILD_TESTS)
    enable_testing()
    add_executable(aurions_core_smoke_test
        core/cpp/tests/version_test.cpp
    )
    target_link_libraries(aurions_core_smoke_test PRIVATE aurions_core)
    add_test(NAME aurions.core.smoke COMMAND aurions_core_smoke_test)
endif()
