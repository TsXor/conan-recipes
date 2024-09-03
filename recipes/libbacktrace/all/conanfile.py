import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, check_min_vs


required_conan_version = ">=1.54.0"


class LibbacktraceConan(ConanFile):
    name = "libbacktrace"
    description = "A C library that may be linked into a C/C++ program to produce symbolic backtraces."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ianlancetaylor/libbacktrace"
    topics = ("backtrace", "stack-trace")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "random_seed": ["ANY"],
    }
    default_options = {
        "shared": False,
        "random_seed": "libbacktrace",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            check_min_vs(self, "180")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_SHARED"] = self.options.shared
        tc.cache_variables["RANDOM_SEED_STRING"] = self.options.random_seed
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["backtrace"]
        self.cpp_info.set_property("cmake_file_name", "libbacktrace")
        self.cpp_info.set_property("cmake_target_name", "libbacktrace::backtrace")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package_multi"] = "package"
