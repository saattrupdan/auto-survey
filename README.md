# AutoSurvey

Conduct your literature survey in 10 minutes for $0.05.

______________________________________________________________________
[![Code Coverage](https://img.shields.io/badge/Coverage-0%25-red.svg)](https://github.com/saattrupdan/auto-survey/tree/main/tests)
[![Documentation](https://img.shields.io/badge/docs-passing-green)](https://saattrupdan.github.io/auto-survey)
[![License](https://img.shields.io/github/license/saattrupdan/auto-survey)](https://github.com/saattrupdan/auto-survey/blob/main/LICENSE)
[![LastCommit](https://img.shields.io/github/last-commit/saattrupdan/auto-survey)](https://github.com/saattrupdan/auto-survey/commits/main)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](https://github.com/saattrupdan/auto-survey/blob/main/CODE_OF_CONDUCT.md)

Developer:

- Dan Saattrup Smart (<saattrupdan@gmail.com>)

## Getting Started

### Get a Semantic Scholar API key

The first thing to do is to [request an API key for Semantic
Scholar](https://www.semanticscholar.org/product/api#api-key-form). Note that this can
only be used for research purposes. Here are some suggested answers for the form:

```text
> How do you plan to use Semantic Scholar API in your project? (50 words or more)*

Creating literature surveys using the AutoSurvey package.

> Which endpoints do you plan to use?

The /paper/search endpoint.

> How many requests per day do you anticipate using?

Around 100 requests per day.
```

When you have it, you create a file called `.env` in your current directory with the
following content:

```text
SEMANTIC_SCHOLAR_API_KEY="<your key here>"
```

If you already had a `.env` file, you can just append the line above to it.

### Set up an LLM API key

Next, you need to set up an API key for the large language model (LLM) that you want to
use. The default model is `gpt-4.1-mini` from OpenAI, which requires you to have an OpenAI
API key, and again add it to your `.env` file:

```text
OPENAI_API_KEY="<your key here>"
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

## Using Different Model Providers

The package supports all of [LiteLLM's
providers](https://docs.litellm.ai/docs/providers/), including OpenAI, Anthropic,
Google, xAI, local models, and more. You can simply set the `--model` argument to the
model you want to use. For example, to use Claude Sonnet 4.5 from Anthropic, use

```bash
uvx auto-survey "<your topic here>" --model "claude-sonnet-4-5"
```

Some providers require you to prefix the model ID with the provider name. For instance,
to use the Grok-3-mini model from xAI, you need to use

```bash
uvx auto-survey "<your topic here>" --model "xai/grok-3-mini"
```

All of this is documented in the [LiteLLM provider
documentation](https://docs.litellm.ai/docs/providers). If you use a different provider,
you need to set different environment variables. See the [LiteLLM provider
documentation](https://docs.litellm.ai/docs/providers) for more information on which
environment variables to set.

### Custom Inference API

You can also run the package with a custom inference API. In this case you need to set
the `--base-url` argument with the URL to the inference API, and also set the
`--api-key-env-var` argument with the name of the environment variable that contains the
API key for the inference API. This variable must again be set in the `.env` file:

```text
<value-of-api-key-env-var>="<your key here>"
```

Lastly, when using custom inference APIs, you need to use a custom prefix as well,
dependending on what kind of inference server you're using. If it is running with vLLM,
you need to use the `hosted_vllm/` prefix, for instance, and Ollama models use the
`ollama_chat/` prefix. See the [LiteLLM provider
documentation](https://docs.litellm.ai/docs/providers) for more information on which
prefixes to use.
