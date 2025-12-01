# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fixed an issue where we would always look for more papers, even when there aren't any
  relevant ones left. This usually happened if the topic was very niche.

## [v0.2.0] - 2025-10-10

### Changed

- We now re-create the References section manually, which ensures consistent formatting,
  correct alphabetical order, and only includes references that were actually cited in
  the literature survey.
- We've added a logo now, and hidden many of the logs. These can be shown with the
  `--verbose` flag.
- We now use the WeasyPrint PDF engine when converting the Markdown literature survey to
  PDF rather than PDFLaTeX, as the latter often had issues with Unicode characters.
- We now check whether `pandoc` and `weasyprint` are installed before attempting to
  convert the generated Markdown survey into PDF, and give an informative error message
  describing how to install these.
- Sometimes the LLMs add a note at the end of the paper. We have now added to the
  writing prompt to refrain from doing this. This might still happen, but the
  probability should be a lot lower now.

### Fixed

- Fixed a bug related to the parsing of the PDFs of some papers, due to the file not
  ending in `.pdf`. This has been fixed now.
- We now catch `docling.ConversionError` during parsing of PDF files, and skip those
  files instead of crashing.
- We now catch all `httpx.RequestError` during fetching of PDF files, and skip those
  files instead of crashing.
- We now catch `CalledProcessError` during conversion to PDF, and give an informative
  error message instead of crashing.
- We now use `docling>=2.55.0` as errors appeared in earlier versions, as they
  refactored their code base.

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
