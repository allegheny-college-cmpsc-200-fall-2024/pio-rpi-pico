import os
import sys

from platformio.proc import exec_command
from SCons.Script import DefaultEnvironment, Builder, Import

def print_output(output: list = []) -> None:
    for line in output.split("\n"):
        print(line)

# Shouts to the real ones working on the ESP32 PIO Framework:
# https://github.com/platformio/platform-espressif32/blob/de553ce4a8592fc140098a767dccf4d5f56ef191/builder/frameworks/espidf.py#L822

# I was also unintentionally building the same thing as WizIO wih some slight variations
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
        if file == "CMakeLists.txt":
            os.chdir(build_dir)
            cmd = [
                os.path.join(platform.get_package_dir("tool-cmake") or "", "bin", "cmake"),
                project_dir,
                f"-D CMAKE_C_COMPILER = {cc}",
                f"-D CMAKE_CXX_COMPILER = {cxx}"
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

            # Assess size of binary, taken from:
            # https://github.com/Wiz-IO/wizio-RPI/blob/main/builder/frameworks/build-pico-cmake.py

            env.Execute("$SIZETOOL -B "+ os.path.join(env.subst("$BUILD_DIR"),"${PROGNAME}.elf"), None)

            # Could probably remove the directory jitterbug
            os.chdir(project_dir)

print("Importing environment...")

Import('env')

platform = env.PioPlatform()
os.environ["PICO_SDK_PATH"] = env["PICO_SDK_PATH"]
build_dir = env.subst("$BUILD_DIR")
project_dir = env.subst("$PROJECT_DIR")

print("Substituting new compiler action...")
env.Replace(
    PROGSUFFIX = '',
    PIOBUILDFILES = [],
    UPLOADCMD = '',
    BUILDERS = dict(
        ACT = Builder(
            action = env.VerboseAction(
                run_cmake,
                None
            ),
            suffix = '.none'
        )
    )
)

env.ACT()
