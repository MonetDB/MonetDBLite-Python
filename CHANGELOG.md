# Changelog
All notable changes in this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
## 0.6.3
### Added
- Coverage reports from OS X with [codecov](https://codecov.io/gh/MonetDB/MonetDBLite-Python)
### Changed
- Reworked the build system to use
  [cibuildwheel](https://github.com/joerick/cibuildwheel) (fixed #18).
  This essentially means that we now provide binary wheels for the
  following platforms:
  + GNU/Linux x86_64
    - Python 2.7
    - Python 3.5
    - Python 3.6
    - Python 3.7
  + GNU/Linux x86_64
    - Python 2.7
    - Python 3.5
    - Python 3.6
    - Python 3.7
  + MacOS X 10.6 Intel
    - Python 2.7
    - Python 3.5
    - Python 3.6
    - Python 3.7
  + Windows AMD64
    - Python 3.5
    - Python 3.6
    - Python 3.7
- Fixed the iterator protocol for cursors (fixed #34)
- Fixed a bug about inserting nulls using `monetdblite.insert` (fixed
  #32)
- `monetdblite.init` can now be called with relative paths (fixed #28)
- Deprecated support for Python 2.7. Starting from the next feature
  release (version 0.7.0), we are going to offer binary wheels only
  for python versions >= 3.5
- Deprecated support for 32 bit builds. Starting from the next
  feature release (version 0.7.0) we are goint to offer binary wheels
  only for 64 bit platforms.
- Changed test fixtures to use pytest's temporary file generation
  facilities.
### Removed
- Builds for 32 bit Windows. Building MonetDBLite-C for 32 bit
  Windows, requires a lot of work for too little benefit.
## 0.6.2
### Added
- Added Python 3.7 to the build matrix
- Added changelog.
### Removed
- Builds for Python 2.7 and 3.4 on Windows: MonetDBLite-C cannot be
  compiled by the MSVC compiler version required for these Python
  versions.
### Changed
- Updated MonetDBLite-C library to Aug2018 branch: Commit
  [d8b1b5e729678923a7f1a52eff9c775519eb8b5e](https://github.com/hannesmuehleisen/MonetDBLite-C/commit/d8b1b5e729678923a7f1a52eff9c775519eb8b5e)
- Ported test suite in pytest
- Moved from mingw to Visual Studio for windows builds
