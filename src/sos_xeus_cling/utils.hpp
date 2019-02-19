#include <iostream>
#include <typeinfo>
#include <cstdlib>
#include <memory>
#include <cxxabi.h>
#include "xtensor/xarray.hpp"
#include "xtensor/xio.hpp"
#include "xtensor/xview.hpp"
#include "xtensor/xrandom.hpp"
#include "xframe/xio.hpp"
#include "xframe/xvariable.hpp"

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

//Print row and column labels of xframe
//Rework of view function from here: https://github.com/QuantStack/xframe/blob/e16299b1f572a98e4ac77010f646c0f99cf3e855/include/xframe/xio.hpp#L26 
template <class T> 
void print_dataframe_indices(const T& expr, const int& dim)
{
    const auto& dim_name = expr.dimension_mapping().labels()[dim];

    for (std::size_t row_idx = 0; row_idx < expr.shape()[dim]; ++row_idx)
    {
        xtl::visit([](auto&& arg) { std::cout << "\"" << arg << "\","; }, expr.coordinates()[dim_name].label(row_idx));
    }

}