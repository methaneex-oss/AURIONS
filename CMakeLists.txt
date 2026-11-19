cmake_minimum_required(VERSION 3.20)

project(AURIONS VERSION 0.1.0 LANGUAGES CXX)

include(CTest)
find_package(SQLite3 REQUIRED)

add_library(aurions_core
    core/cpp/src/experience_store.cpp
)
target_include_directories(aurions_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/include>
)
target_compile_features(aurions_core PUBLIC cxx_std_20)
target_link_libraries(aurions_core PUBLIC SQLite::SQLite3)
set_target_properties(aurions_core PROPERTIES CXX_EXTENSIONS OFF)

add_executable(aurions
    core/cpp/src/main.cpp
)
target_link_libraries(aurions PRIVATE aurions_core)

if(BUILD_TESTING)
    find_package(Python3 COMPONENTS Interpreter REQUIRED)
    add_test(
        NAME aurions.experience.process_restart
        COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/tests/experience_store_integration.py
            $<TARGET_FILE:aurions>
    )
endif()
