# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Builder, Default, DefaultEnvironment)

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("pico-sdk")
env["PICO_SDK_PATH"] = FRAMEWORK_DIR

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    SIZEPROGREGEXP=r"^(?:\.text|\.data|\.rodata|\.text.align|\.ARM.exidx)\s+(\d+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    PROGSUFFIX=".elf"
)

env.Append(
    BUILDERS = dict(
        Silent=Builder(
            action = env.VerboseAction("".join([
                platform.get_package_dir("tool-cmake"),
                env.subst("$PROJECT_DIR"),
                f"-D CMAKE_C_COMPILER = $CC",
                f"-D CMAKE_CXX_COMPILER = $CXX"
            ]),
            "Running a thing.")
        )
    )
)

# Call cmake and make
env.SConscript("frameworks/baremetal.py", exports = "env")

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = os.path.join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = os.path.join("$BUILD_DIR", "${PROGNAME}.bin")
else:
    target_elf = env.BuildProgram()
    target_firm = env.Silent(os.path.join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    env.Depends(target_firm, "checkprogsize")

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)

# Assess size of binary

target_size = env.Alias(
    "size", env.BuildProgram(),
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE")
)
AlwaysBuild(target_size)

# Setup picoprobe debug
env.Replace(
    UPLOADER = os.path.join(platform.get_package_dir("tool-rp2040tools")),
    UPLOADER_FLAGS = ["-v","-D"],
    UPLOADCMD = "$UPLOADER $UPLOADERFLAGS $SOURCES"
)

# Need to calculate the binary size, but avoid the stock build step:
# https://github.com/platformio/platform-espressif32/blob/de553ce4a8592fc140098a767dccf4d5f56ef191/builder/main.py#L392

