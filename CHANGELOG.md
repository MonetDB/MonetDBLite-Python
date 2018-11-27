# Changelog
All notable changes in this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
## Added
- Coverage reports when running the test suite with py37
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
