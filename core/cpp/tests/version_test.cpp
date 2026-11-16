#include "aurions/version.hpp"

#include <cstdlib>
#include <iostream>

int main() {
    if (aurions::version() != "0.1.0") {
        std::cerr << "Unexpected AURIONS core version\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
