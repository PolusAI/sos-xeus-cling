#include <iostream>
#include <typeinfo>
#include <cstdlib>
#include <memory>
#include <cxxabi.h>
std::string demangle(const char* name) {
    int status = -4; // some arbitrary value to eliminate the compiler warning
    std::unique_ptr<char, void(*)(void*)> res {
        abi::__cxa_demangle(name, NULL, NULL, &status),
        std::free
    };
    return (status==0) ? res.get() : name ;
}
template<class T> std::string type(const T& t) {
    return demangle(typeid(t).name());
}

// #define typename(x) _Generic((x),                                                 \
//          bool: "_Bool",                  unsigned char: "unsigned char",          \
//          char: "char",                     signed char: "signed char",            \
//     short int: "short int",         unsigned short int: "unsigned short int",     \
//           int: "int",                     unsigned int: "unsigned int",           \
//      long int: "long int",           unsigned long int: "unsigned long int",      \
// long long int: "long long int", unsigned long long int: "unsigned long long int", \
//         float: "float",                         double: "double",                 \
//   long double: "long double",                   char *: "pointer to char",        \
//        void *: "pointer to void",                int *: "pointer to int",         \
//       default: "other")