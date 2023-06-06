# pyBDY contribution guidelines

## Set up a development conda environment

Before making any changes to the code, it is recommended to create a new conda environment for development:

```bash
conda env create -n pybdy-dev -f environment.yml python=3.9
conda activate pybdy-dev
```

## Create a branch to work on an issue

If you don't have write permissions on NOC-MSM/pyBDY, fork the repository and work from your own fork.

1. Open a GitHub issue or pick one already opened
1. Create a branch that references the issue number and gives a summary of the changes that will be made:  `git branch issue-103-remove-pynemo-traces`
1. Switch to that branch (i.e., update HEAD to set that branch as the current branch): `git checkout issue-103-remove-pynemo-traces`
1. Make your changes to the code

## Pre-push steps

Before pushing to GitHub, run the following commands:

1. Update conda environment: `make conda-env-update`
1. Install this package: `pip install -e .`
1. Sync with the latest [template](https://github.com/ecmwf-projects/cookiecutter-conda-package) (optional): `make template-update`
1. Install pre-commit hooks: `pre-commit install`
1. Run quality assurance checks: `make qa`
1. Run tests: `make unit-tests`
1. Run the static type checker (currently not working for pyBDY): `make type-check`
1. Build the documentation (optional, see [Sphinx tutorial](https://www.sphinx-doc.org/en/master/tutorial/)): `make docs-build`

## Push to GitHub

1. Add changes to the staging area with `git add src/pybdy/file_change.py`
1. Commit changes: `git commit -m "#103 Remove pynemo traces"`
1. As hooks are run on every commit because before we executed `pre-commit install`, they may flag problems with the code and/or change some of its parts, thus preventing the commit attempt to be successful. If all pre-commit hooks passed, jump to step 7.
1. Solve any issue flagged by the pre-commit hooks.
1. Update already stag files executing `git add -u`.
1. Commit changes once again `git commit -m "#103 Remove pynemo traces"`.
1. Finally, push changes to GitHub and set the remote as upstream with `git push --set-upstream origin issue-103-remove-pynemo-traces`.

## Make a pull request

Go to the `issue-103-remove-pynemo-traces` branch and make a pull request to master.

## Notes

- Pre-commit hooks can be run at any stage during development. To run them, use `pre-commit run --all-files` or `make qa`. If you want to just run the pre-commit hooks on a specific file, use `pre-commit run --files path_to_file.py`.
