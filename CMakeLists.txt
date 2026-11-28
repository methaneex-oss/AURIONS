cmake_minimum_required(VERSION 3.20)

project(AURIONS VERSION 0.1.0 LANGUAGES CXX)

include(CTest)
find_package(SQLite3 REQUIRED)

# CMake's FindSQLite3 imported-target name varies across supported versions.
if(TARGET SQLite::SQLite3)
    set(AURIONS_SQLITE_TARGET SQLite::SQLite3)
elseif(TARGET SQLite3::SQLite3)
    set(AURIONS_SQLITE_TARGET SQLite3::SQLite3)
else()
    message(FATAL_ERROR "FindSQLite3 did not provide a supported imported target")
endif()

add_library(aurions_core
    core/cpp/src/belief_store.cpp
    core/cpp/src/experience_store.cpp
    core/cpp/src/inference_adapter.cpp
    core/cpp/src/memory_context.cpp
    core/cpp/src/strategy_store.cpp
)
target_include_directories(aurions_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/include>
)
target_compile_features(aurions_core PUBLIC cxx_std_20)
target_link_libraries(aurions_core PUBLIC ${AURIONS_SQLITE_TARGET})
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
    add_test(
        NAME aurions.inference.process_preview
        COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/tests/inference_adapter_integration.py
            $<TARGET_FILE:aurions>
    )
    add_test(
        NAME aurions.cognition.quarantined_preview
        COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/tests/cognition_preview_integration.py
            $<TARGET_FILE:aurions>
    )
    add_test(
        NAME aurions.cognition.durable_chat
        COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/core/cpp/tests/cognition_chat_integration.py
            $<TARGET_FILE:aurions>
    )
endif()
