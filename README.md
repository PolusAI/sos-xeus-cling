[![Build Status](https://travis-ci.com/LabShare/sos-xeus-cling.svg?branch=master)](https://travis-ci.com/LabShare/sos-xeus-cling)
[![PyPI version](https://badge.fury.io/py/sos-xeus-cling.svg)](https://badge.fury.io/py/sos-xeus-cling)

# sos-xeus-cling
## SoS extension for C++. Developed independently from original SoS team. Please refer to [SoS Homepage](http://vatlab.github.io/SoS/) for details.

This language extension to SoS allows to use C++ with xeus-cling Jupyter kernel (https://github.com/QuantStack/xeus-cling) and exchange variables with other languages in Polyglot environment

### Dependencies

* gcc 
`apt-get update; apt-get install gcc`
* xeus-cling
`conda install xeus-cling xwidgets notebook xtensor xtl xframe -c conda-forge/label/gcc7`
* sos-notebook `pip install sos-notebook --upgrade; python -m sos_notebook.install`

### Install
`pip install sos-xeus-cling`

### Supported variable types for transfer

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
| `std::map`     | `dict`                         |
| `std::vector`  | `numpy.ndarray`                |
| Xtensor          | `numpy.ndarray`                |
| Xframe         | `pandas.DataFrame`             |
