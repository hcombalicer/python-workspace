# python-workspace
Python Codes for Google Workspace

## Developing in codespace
1. Make sure you are on the `main` branch (or the branch you want to branch off from):
`git checkout main`
2. Create and switch to the new branch:
`git checkout -b test-branch`
3. Make the code changes.
1. `git status`
2. `git add .` (add all the files in the current directory) / git add <filename1> <filename1>
3. `git commit -m "Your concise commit message here"`
4. A pre-commit check should run to check the staged items. You can only proceed if all the checks are passed. If a file has been updated or modified automatically by the linter, you need to run again `git add .` to ensure that the changes is applied on your next `git commit`.
5. Push your new local branch to the remote repository (creating it there if it doesn't exist):
`git push origin test-branch` or with tracking: `git push -u origin test-branch`

## Developing locally

## Pre-commit configuration
1. Create the file: Create a file named `.pre-commit-config.yaml` in the root directory of your GitHub repository. ([sample](.pre-commit-config.yaml))
2. Install `pre-commit`:
`pip install pre-commit`
3. Install the Git hooks: Run the following command in your repository's root directory:
`pre-commit install`
4. Run against all files (optional): To check all your files initially, you can run:
`pre-commit run --all-files`
