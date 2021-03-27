# CSS Compare

A command-line application to compare two CSS scripts to find functional (as opposed to structural) differences.

## The Problem

Two CSS scripts that apply the same formatting to the exact same elements can be structured completely differently. Because of this, standard text diff programs are close to useless for answering the question, "what are the differences between these files?"

This application aims to parse the CSS rules in each file, compare them in a systematic way, and report accurately the selectors and rules which are truly different between the two. Currently this analysis is incomplete (particularly for rules), mainly in cases where things that should compare as equal are still reported as differences.

Built using the [tinycss](http://pythonhosted.org/tinycss) library.

## Setup

#### Clone the repository

#### Create a virtual environment

Not essential but highly recommended. There are many different ways to do this, the simplest is to
use the python built-in module.

```sh
python -m venv ./.venv
```

(The above assumes you want the files for the virtual environment in the `./.venv` library,
you can actually put them anywhere.)

#### Install Dependencies

```sh
pip install --upate pip setuptools wheel pip-tools

pip-compile *.in

pip-sync requirements.txt dev-requirements.txt
```
