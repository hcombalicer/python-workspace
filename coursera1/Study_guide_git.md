# Study guide: Git

In any Git project, there are three sections: the Git directory,
the working tree, and the staging area. This study guide provides some
basic concepts and commands that can help you get started with Git as
 well as guidelines to help you write an effective commit message.

### Git config command

The Git config command is used to set the values to identify who made changes to Git repositories. To set the values of user.email and user.name to your email and name, type: 

`: ~$ git config  - -global user.email “me@example.com”`

`: ~$ git config  - -global user.name “My name”`

### Git init command

`: ~/checks$ git init`

The Git init command can create a new empty repository in a current
directory or re-initialize an existing one.

### Git ls -la command

`: ~/checks$ ls -la`

The Git ls - la command checks that an identified directory exists.

`: ~/checks$ ls -l .git/`

The ls-l.git command checks inside the directory to see the different
things that it contains. This is called the Git directory.
The Git directory is a database for your Git project that stores
the changes and the change history.

### Git add command

`:~/checks$ git add disk_usage.py`

Using the Git add command allows Git to track your file and uses
the selected file as a parameter when adding it to the staging area.
The staging area is a file maintained by Git that contains all the
information about what files and changes are going to go into your
next commit.

### Git status command

`:~/checks$ git status`

The Git status command is used to get some information
about the current working tree and pending changes.

### Git commit command

`:~/checks$ git commit`

The .git commit command is run to remove changes made
from the staging area to the .git directory. When this command is run,
it tells Git to save changes. A text editor is opened that allows a
commit message to be entered.

## Guidelines for writing commit messages

A commit message is generally broken into two sections:
a short summary and a description of the changes. When the git commit
command is run, Git will open a text editor to write your commit message.
A good commit message includes the following:

__Summary:__ The first line contains the summary, formatted as a header,
containing 50 characters or less.

__Description:__ The description is usually kept under 72 characters
and provides detailed information about the change. It can include
references to bugs or issues that will be fixed with the change.
It also can include links to more information when relevant.

Click the link to review an example of a commit message:
https://commit.style/

### Key takeaways

Knowing basic Git commands and guidelines for writing better messages can help you get started with Git as well as better communicate with others.

## Study guide: Advanced Git

| Command | Explanation & Link |
| --- | --- |
| git commit -a | [git commit -a](git commit -a) automaticallystages the files that have been locally modified. New files which have not been published yet are not affected. |
| git log -p | [git log -p](git log -p) produces patch text that displays the lines of code that were changed in each commit in the current repo. |
| git show | [git show](git show) shows you one or more object(s) such as blobs, trees, tags, and commits. |
| git diff | [git diff](git diff) is similar to the Linux `diff` command, and can show the changes between commits, changes between the working tree and index, changes between two trees, changes from a merge, and so on. |
| git diff --staged | [git diff --staged](git diff --staged) is an alias of |
| git add -p | [git add -p](git add -p) allows a user to interactively review patches before adding to the current commit. |
| git mv | [git mv](git mv) is similar to the Linux `mv` command. This command can move or rename a file, directory, or symlink. |
| git rm | [git rm](git rm) is similar to the Linux `rm` command. This command deletes or removes a file from the working tree. |

There are many useful git command summaries online as well.
Please take some time to research and study a few, such as this one.

## .gitignore files

.gitignore files are used to tell the git tool to intentionally ignore
some files in a given Git repository. For example, this can be useful
for configuration files or metadata files that a user may not want to
check into the master branch.

When writing a .gitignore file, there are some specific formats
which help tell Git how to read the text in the file. For example,
a line starting with # is a comment; a slash / is a directory separator.
Visit [https://git-scm.com/docs/gitignore](https://git-scm.com/docs/gitignore)
to see more examples.

When writing a .gitignore file, there are some specific formats
which help tell Git how to read the text in the file. For example,
a line starting with # is a comment; a slash / is a directory separator.
Visit [https://git-scm.com/docs/gitignore](https://git-scm.com/docs/gitignore)
to see more examples.

## Study guide: Git Revert

When writing and committing code, making mistakes is a common occurrence.
Thankfully, there are multiple ways for you to revert or undo your mistakes.
Take a look at the helpful commands below.

[git checkout](https://git-scm.com/docs/git-checkout) is used to switch
branches. For example, you might want to pull from your main branch.
In this case, you would use the command `git checkout main`.
This will switch to your main branch, allowing you to pull.
Then you could switch to another branch by using the command
`git checkout <branch>`.

[git reset](https://git-scm.com/docs/git-reset#_examples)  can be
somewhat difficult to understand. Say you have just used the command
`git add` to stage all of your changes, but then you decide that you
are not ready to stage those files. You could use the command `git reset`
to undo the staging of your files.

There are some other useful articles online, which discuss more aggressive
approaches to [resetting the repo](https://jwiegley.github.io/git-from-the-bottom-up/3-Reset/4-doing-a-hard-reset.html)
(Git repository). As discussed in this article, doing a hard reset can
be extremely dangerous. With a hard reset, you run the risk of losing your
local changes. There are safer ways to achieve the same effect. For example,
you could run `git stash`, which will temporarily shelve or stash your
current changes. This way, your current changes are kept safe, and you
can come back to them if needed.

[git commit --amend](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---amend)
is used to make changes to your most recent commit after-the-fact,
which can be useful for making notes about or adding files to your
most recent commit. Be aware that this `git --amend` command rewrites
and replaces your previous commit, so it is best not to use this
command on a published commit.

[git revert](https://git-scm.com/docs/git-revert) makes a new commit
which effectively rolls back a previous commit. Unlike the `git reset`
command which rewrites your commit history, the `git revert`
command creates a new commit which undoes the changes
in a specific commit. Therefore, a `revert` command is generally safer
than a `reset` command.

For more information on these and other methods to undo something in Git,
checkout this [Git Basics - Undoing Things](https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things)
article.

Additionally, there are some interesting considerations about how git object data is stored, such as the usage of SHA-1.

SHA-1 is what’s known as a *hash function*, a cryptographic function
that generates a digital fingerprint of a file.
Theoretically, it’s impossible for two different files to have the
same SHA-1 hash, which means that SHA-1 can be used for two things:

* Confirming that the contents of a file have not changed
(digital signature).
* Serving as an identifier for the file itself (a token or fingerprint).

Git calculates a hash for every commit. Those hashes are displayed by
commands like `git log` or in various pages on Github. For commands
like `git revert`, you can then use the hash to refer to a specific commit.

Feel free to read more here:

* [SHA-1 collision detection on GitHub.com](https://github.blog/2017-03-20-sha-1-collision-detection-on-github-com/)

Even the most accomplished developers make mistakes in Git.
It happens to everyone, so don’t stress about it. You have these
and other methods to help you revert or undo your mistakes.

## Study guide: Git branches and merging

Now that you’ve learned about branches and merging, use this study guide
as an easy reference for Git branching. This study guide gives a
brief explanation of these useful commands along with a link to the
Git documentation for each command. Keeping study guides like this one
easily accessible can help you code more efficiently.

| Command                      | Explanation                                                                                                                                                                  |
| :--------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `git branch`                 | Can be used to list, create, or delete branches.                                                                                                                               |
| `git branch <name>`          | Can be used to create a new branch in your repository.                                                                                                                         |
| `git branch -d <name>`       | Can be used to delete a branch from your repository.                                                                                                                            |
| `git branch -D <branch>`     | Forces a branch to be deleted.                                                                                                                                              |
| `git checkout <branch>`      | Switches your current working branch.                                                                                                                                      |
| `git checkout -b <new-branch>` | Creates a new branch and makes it your current working branch.                                                                                                           |
| `git merge <branch>`         | Joins changes from one branch into another branch.                                                                                                                            |
| `git merge --abort`          | Can only be used after merge conflicts. This command will abort the merge and try to go back to the pre-merge state.                                                          |
| `git log --graph`            | Prints an ASCII graph of the commit and merge history.                                                                                                                        |
| `git log --oneline`          | Prints each commit on a single line.

Keep this table handy while you are getting comfortable using Git
branches and merging. Now, it’s time to put your newfound knowledge
of Git branches and merging to use!
                                                                                                                        |