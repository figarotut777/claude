cmake_minimum_required(VERSION 3.22)

project(LA2A_COMPRESSOR VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# JUCE setup - you need to have JUCE in your system or as a submodule
# Option 1: Set JUCE_DIR to your JUCE installation
# Option 2: Use FetchContent (uncomment below)

# Uncomment to fetch JUCE automatically:
# include(FetchContent)
# FetchContent_Declare(
#     JUCE
#     GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
#     GIT_TAG 7.0.9
# )
# FetchContent_MakeAvailable(JUCE)

# Or set manually:
# set(JUCE_DIR "/path/to/JUCE" CACHE PATH "Path to JUCE")
# add_subdirectory(${JUCE_DIR} JUCE)

# For this example, assume JUCE is available
find_package(JUCE CONFIG REQUIRED)

juce_add_plugin(LA2ACompressor
    COMPANY_NAME "YourCompany"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD TRUE
    PLUGIN_MANUFACTURER_CODE Manu
    PLUGIN_CODE La2a
    FORMATS VST3 AU Standalone
    PRODUCT_NAME "LA-2A Optical Compressor")

target_sources(LA2ACompressor
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginEditor.cpp
        Source/DSP/OptoCell.cpp
        Source/DSP/TubeSaturation.cpp
        Source/DSP/TransformerModel.cpp
        Source/DSP/Oversampling.cpp)

target_compile_definitions(LA2ACompressor
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0)

target_link_libraries(LA2ACompressor
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
