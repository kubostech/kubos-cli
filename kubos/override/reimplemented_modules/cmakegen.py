# Kubos SDK
# Copyright (C) 2017 Kubos Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from yotta.lib.cmakegen import *


class KubosCMakeGen(CMakeGen):
    def _kCheckImmediateDeps(self, deps):
        # make a copy so we don't recurse
        new_deps = {}
        dep_items = [i for i in deps.items()]
        for name, component in dep_items:
            if component.isTestDependency():
                continue
            if component.getLinkWholeArchive():
                # surround 'whole archive' libs with the proper linker args
                new_key = ('${YOTTA_LINK_WHOLE_ARCHIVE_PRE} '
                           '%s ${YOTTA_LINK_WHOLE_ARCHIVE_POST}') % name
                new_deps[new_key] = deps[name]
            else:
                new_deps[name] = deps[name]

        return new_deps

    def generateSubDirList(self, builddir, dirname, source_files, component,
                           all_subdirs, immediate_dependencies, object_name,
                           resource_subdirs, is_executable):

        deps = self._kCheckImmediateDeps(immediate_dependencies)
        return super(KubosCMakeGen, self).generateSubDirList(builddir, dirname,
                                                             source_files,
                                                             component,
                                                             all_subdirs,
                                                             deps, object_name,
                                                             resource_subdirs,
                                                             is_executable)


CMakeGen = KubosCMakeGen
