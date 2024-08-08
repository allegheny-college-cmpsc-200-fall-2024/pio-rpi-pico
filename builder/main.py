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
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

# Initialize defaults
env = DefaultEnvironment()
program = None

# This file, HUH, what is it good for? Absolutely one thing (SAY IT AGAIN!)
env.ProcessProgramDeps()

# The environment built by the framework file needs to return here; otherwise
# the build fails due to the environment's lack of awareness about the built
# products.

# Assess size of binary, taken from:
# https://github.com/Wiz-IO/wizio-RPI/blob/main/builder/frameworks/build-pico-cmake.py

prog_size = "$SIZETOOL -B "+ os.path.join(env.subst("$BUILD_DIR"),"${PROGNAME}.elf")
check_prog_size = env.Alias("checkprogsize",os.path.join(env.subst("$BUILD_DIR"),"${PROGNAME}.elf"),[env.VerboseAction(prog_size, "Done.")])

