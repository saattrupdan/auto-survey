<!-- This disables the "First line in file should be a top level heading" rule -->
<!-- markdownlint-disable MD041 -->
<a href="https://github.com/alexandrainst/auto_survey">
<img
 src="https://filedn.com/lRBwPhPxgV74tO0rDoe8SpH/alexandra/alexandra-logo.jpeg"
 width="239"
 height="175"
 align="right"
 alt="Alexandra Institute Logo"
/>
</a>

# AutoSurvey

Automated literature surveys.

______________________________________________________________________
[![Code Coverage](https://img.shields.io/badge/Coverage-0%25-red.svg)](https://github.com/alexandrainst/auto_survey/tree/main/tests)
[![Documentation](https://img.shields.io/badge/docs-passing-green)](https://alexandrainst.github.io/auto_survey)
[![License](https://img.shields.io/github/license/alexandrainst/auto_survey)](https://github.com/alexandrainst/auto_survey/blob/main/LICENSE)
[![LastCommit](https://img.shields.io/github/last-commit/alexandrainst/auto_survey)](https://github.com/alexandrainst/auto_survey/commits/main)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](https://github.com/alexandrainst/auto_survey/blob/main/CODE_OF_CONDUCT.md)

Developer:

- Dan Saattrup Smart (<saattrupdan@gmail.com>)

## Quickstart

### Get a Semantic Scholar API key

The first thing to do is to [request an API key for Semantic
Scholar](https://www.semanticscholar.org/product/api#api-key-form). Here are some
suggested answers for the form:

```text
> How do you plan to use Semantic Scholar API in your project? (50 words or more)*

Creating literature surveys using the AutoSurvey package.

> Which endpoints do you plan to use?

The /paper/search endpoint.

> How many requests per day do you anticipate using?

Around 100 requests per day.
```

### Installing and Running

The easiest way to use the package is as a
[uv](https://docs.astral.sh/uv/getting-started/installation/) tool. You can simply start
searching for properties using the following command:

```bash
uvx auto-survey "<your topic here>"
```

This both installs the package and creates the literature survey. All the available
options are listed below, but you can always get these by running the following command:

```bash
uvx auto-survey --help
```
