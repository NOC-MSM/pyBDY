# pyBDY contribution guidelines

## Set up a development conda environment

It is recommended to create a new conda environment for development:

```bash
conda env create -n pybdy-dev python=3.9
conda env update -n pybdy-dev -f environment.yml
conda activate pybdy-dev
```

## Clone the repository and install pre-commit hooks

If you don't have write permissions on [NOC-MSM/pyBDY](https://github.com/NOC-MSM/pyBDY), fork the repository and work from your own fork.

1. Clone the repository, e.g.: `git clone git@github.com:NOC-MSM/pyBDY.git`
1. Move to the repository: `cd pyBDY`
1. Install pre-commit hooks: `pre-commit install`

# New features and code improvements

## Create a branch to work on an issue

1. Update the master branch of your local repository: `git checkout master && git pull`
1. Open a GitHub issue or pick one already opened
1. Create a branch that references the issue number and gives a summary of the changes that will be made:  `git branch issue-103-remove-pynemo-traces`
1. Switch to that branch (i.e., update HEAD to set that branch as the current branch): `git checkout issue-103-remove-pynemo-traces`

## Stage and commit changes

1. Make your changes to the code
1. Add changes to the staging area: `git add src/pybdy/file_change.py`
1. Commit changes: `git commit -m "#103 Remove pynemo traces"`
1. As hooks are run on every commit because before we executed `pre-commit install`, they may flag problems with the code and/or change some of its parts, thus preventing the commit attempt to be successful. If all pre-commit hooks passed, go to step 8.
1. Solve any issues flagged by the pre-commit hooks
1. Update already staged files: `git add -u`
1. Commit changes once again: `git commit -m "#103 Remove pynemo traces"`
1. Merge the remote master branch into your local branch: `git fetch && git merge origin/master` (you may need to [solve merge conflicts](<(https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line)>) at this step)

## Pre-push steps

Before pushing to GitHub, run the following commands:

1. Update the conda environment: `make conda-env-update`
1. Install this package: `pip install -e .`
1. Sync with the latest [template](https://github.com/ecmwf-projects/cookiecutter-conda-package) (optional): `make template-update`
1. Run quality assurance checks: `make qa`
1. Run tests: `make unit-tests`
1. Run the static type checker (currently not working for pyBDY): `make type-check`
1. Build the documentation (optional, see [Sphinx tutorial](https://www.sphinx-doc.org/en/master/tutorial/)): `make docs-build`

If changes need to be made in one of these steps, make sure that they are staged and commited (see the `Stage and commit changes` section).

## Push to GitHub and make a pull request

1. Push changes to GitHub and set the remote as upstream: `git push --set-upstream origin issue-103-remove-pynemo-traces`
1. Go to the `issue-103-remove-pynemo-traces` branch and make a pull request to master

## Notes

- Pre-commit hooks can be run at any stage during development. To run them, type `pre-commit run --all-files` or `make qa`. If you just want to run the pre-commit hooks on a specific file, type `pre-commit run --files path_to_file.py`.
- When working in a branch for a substantial amount of time, try to regularly merge the remote master branch into your local branch to avoid significant divergences between both: `git fetch && git merge origin/master`. You may need to [solve conflicts when doing this.](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line)
