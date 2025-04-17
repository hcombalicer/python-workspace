# python-workspace
Python Codes for Google Workspace

## Developing in codespace
1. `git status`
2. `git add .` (add all the files in the current directory) / git add <filename1> <filename1>
3. `git commit -m "Your concise commit message here"`
4. a pre-commit check should run to check the staged items. You can only proceed if all the checks are passed.
5. `git push`

## Developing locally

## Pre-commit configuration
1. Create the file: Create a file named `.pre-commit-config.yaml` in the root directory of your GitHub repository. ([sample](.pre-commit-config.yaml))
2. Install `pre-commit`:
`pip install pre-commit`
3. Install the Git hooks: Run the following command in your repository's root directory:
`pre-commit install`
4. Run against all files (optional): To check all your files initially, you can run:
`pre-commit run --all-files`
