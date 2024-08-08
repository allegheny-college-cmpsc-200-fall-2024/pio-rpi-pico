import os
import sys

from platformio.proc import exec_command
from SCons.Script import AlwaysBuild, DefaultEnvironment, Builder, Import

# Shouts to the real ones working on the ESP32 PIO Framework:
# https://github.com/platformio/platform-espressif32/blob/de553ce4a8592fc140098a767dccf4d5f56ef191/builder/frameworks/espidf.py#L822

# I unintentionally built a similar CMae implementation as WizIO wih some slight variations
# https://github.com/Wiz-IO/wizio-RPI/blob/main/builder/frameworks/build-pico-cmake.py
# My addition(s): the below should work for both C and ASM projects

def run_cmake(*args):
    cc = os.path.join(
        platform.get_package_dir("toolchain-gccarmnoneeabi"),
        "bin",
        "arm-none-eabi-gcc"
    )

    cxx = os.path.join(
        platform.get_package_dir("toolchain-gccarmnoneeabi"),
        "bin",
        "arm-none-eabi-g++"
    )

    for file in os.listdir():
        # Look for CMakeLists file in root of project
        if file == "CMakeLists.txt":
            cmd = [
                os.path.join(platform.get_package_dir("tool-cmake") or "", "bin", "cmake"),
                project_dir,
                #f"-D CMAKE_C_COMPILER = {cc}",
                #f"-D CMAKE_CXX_COMPILER = {cxx}"
            ]

            result = exec_command(cmd, stdout = sys.stdout, stderr = sys.stderr, cwd = build_dir)

            if not result["returncode"] == 0:
                sys.exit(1)

            cmd = [
                "make"
            ]
            result = exec_command(cmd, stdout = sys.stdout, stderr = sys.stderr, cwd = build_dir)

            return

def upload():
    pass

Import("env")

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
)

platform = env.PioPlatform()
os.environ["PICO_SDK_PATH"] = env["PICO_SDK_PATH"]
build_dir = env.subst("$BUILD_DIR")
project_dir = env.subst("$PROJECT_DIR")

print("Updating builder to use CMake...")

env.Replace(
    PROGSUFFIX = '',
    PIOBUILDFILES = [],
    UPLOADCMD = upload,
    BUILDERS = dict(
        CMAKE = Builder(
            action = env.VerboseAction(run_cmake, None),
            suffix = ".none"
        )
    ),
)


run_cmake()
