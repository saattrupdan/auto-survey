# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- We now check whether `pandoc` and `pdflatex` are installed before attempting to
  convert the generated Markdown survey into PDF, and give an informative error message
  describing how to install these.
- We've added a logo now, and hidden many of the logs. These can be shown with the
  `--verbose` flag.
- Removed URLs from the references in the References section.

### Fixed

- Fixed a bug related to the parsing of the PDFs of some papers, due to the file not
  ending in `.pdf`. This has been fixed now.
- We now catch `ConversionError` during parsing of PDF files, and skip those files
  instead of crashing.

## [v0.1.2] - 2025-10-09

### Fixed

- The environment variables where not correctly loaded from the `.env` file. This has
  been fixed now.

## [v0.1.1] - 2025-10-09

### Fixed

- Now sets up logging in the `__init__` file. Previously it was set up in the main
  script, which wasn't triggered properly when `auto-survey` was used with `uvx`.

## [v0.1.0] - 2025-10-09

### Added

- First version of the package, which supports conducting literature surveys with the
  `auto-survey` command.
