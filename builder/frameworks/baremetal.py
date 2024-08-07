import os
import sys

from platformio.proc import exec_command
from SCons.Script import DefaultEnvironment, Import

def print_output(output: list = []) -> None:
    for line in output.split("\n"):
        print(line)

Import('env')

platform = env.PioPlatform()
os.environ["PICO_SDK_PATH"] = env["PICO_SDK_PATH"]
build_dir = env.subst("$BUILD_DIR")
project_dir = env.subst("$PROJECT_DIR")

# Shouts to the real ones working on the ESP32 PIO Framework:
# https://github.com/platformio/platform-espressif32/blob/de553ce4a8592fc140098a767dccf4d5f56ef191/builder/frameworks/espidf.py#L822
gcc = os.path.join(
    platform.get_package_dir("toolchain-gccarmnoneeabi"),
    "bin",
    "arm-none-eabi-gcc"
)

gpp = os.path.join(
    platform.get_package_dir("toolchain-gccarmnoneeabi"),
    "bin",
    "arm-none-eabi-g++"
)

for file in os.listdir():

    if file == "CMakeLists.txt":
        os.chdir(build_dir)
        cmd = [
            os.path.join(platform.get_package_dir("tool-cmake") or "", "bin", "cmake"),
            project_dir,
            f"-D CMAKE_C_COMPILER = {gcc}",
            f"-D CMAKE_CXX_COMPILER = {gpp}",
        ]
        result = exec_command(cmd)
        if not result["returncode"] == 0:
            sys.exit(1)
        print_output(result["out"])
        cmd = [
            "make"
        ]
        result = exec_command(cmd)
        print_output(result["out"])
        os.chdir(project_dir)

# Also worth looking into:
# https://github.com/platformio/platform-espressif32/blob/de553ce4a8592fc140098a767dccf4d5f56ef191/builder/frameworks/espidf.py#L191
