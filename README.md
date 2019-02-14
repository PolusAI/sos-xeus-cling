[![Build Status](https://travis-ci.org/ktaletsk/sos-xeus-cling.svg?branch=dev)](https://travis-ci.org/ktaletsk/sos-xeus-cling)
# sos-xeus-cling
## SoS extension for C++. Developed independently from original SoS team. Please refer to [SoS Homepage](http://vatlab.github.io/SoS/) for details.

This language extension to SoS allows to use C++ with xeus-cling Jupyter kernel (https://github.com/QuantStack/xeus-cling) and exchange variables with other languages in Polyglot environment

**NOTE: early stage development, not ready for use**

### Supported variable types for transfer

Non-implemented type conversions are marked with ❌

#### From SoS to C++ (`%get` magic):

Scalar types

| Source: SoS (Python) type                                                       | Destination: C++ type                  |
|---------------------------------------------------------------------------------|----------------------------------------|
| `int` `long int` `np.intc` `np.intp` `np.int8` `np.int16` `np.int32` `np.int64` | `int` `long int` (depending on value)  |
| `float` `np.float16` `np.float32` `np.float64`                                  | `float` `double`  (depending on value) |
| `np.longdouble`                                                                 | `long double`                          |
| `str`                                                                           | `std::string`                          |
| `bool`                                                                          | `bool`                                 |

Non-scalar types

| Source: SoS (Python) type                             | Destination: C++ type          |
|-------------------------------------------------------|--------------------------------|
| `dict` (only homogeneous keys and values)             | `std::map<key_type, val_type>` |
| Sequence (`list`, `tuple`; only homogeneous elements) | `std::vector<type>`            |
| `numpy.ndarray`                                       | [Xtensor](https://github.com/QuantStack/xtensor) `xt::xarray`           |
| `pandas.DataFrame`                                    | [Xframe](https://github.com/QuantStack/xframe)                         |
|                                                       |                                |

#### From C++ to SoS (`%put` magic):

Scalar types

| Source: C++ type                             | Destination: SoS (Python) type |
|----------------------------------------------|--------------------------------|
| `int` `short int` `long int` `long long int` | `int`                          |
| `float` `double`                             | `float`                        |
| `long double`                                | `np.longdouble`                |
| `char`                                       | `str`                          |
| `bool`                                       | `bool`                         |

Non-scalar types

| Source: C++ type | Destination: SoS (Python) type |
|------------------|--------------------------------|
| ❌`std::map`     | `dict`                         |
| ❌`std::vector`  | `numpy.ndarray`                |
| ❌Xtensor        | `numpy.ndarray`                |
| ❌Xframe         | `pandas.DataFrame`             |
