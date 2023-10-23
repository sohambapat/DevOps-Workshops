

#  AUTOMATING GITHUB FROM WITHIN A CONTAINER


## LEARNING GOALS

In this workshop, you will learn about modifying a container,  passing environment variables into a contianer, and authenticating to an API from within a container, and interacting with the GitHub REST API using `python`.

## Assumptions:  
* [`docker` installed](https://docs.docker.com/get-docker/)
* Workshop-1 completed.
* You are familiar with [REST APIs](https://en.wikipedia.org/wiki/Representational_state_transfer).

## 1. Fork this workshop

Firstly, create a copy of `CSC-519-WS-2` by [forking it](https://en.wikipedia.org/wiki/Fork_(software_development)) to your user account.  Do not change the name.

NOTE: Add the teaching staff as "admin" level collaborators (unity IDs: `mrahman` and `jwore`) under "Settings > Collaborators and Teams."

Check out your fork of `CSC-519-WS-2` locally so you can work with it.


## 2. Set up NC State Github Personal Access Token (PAT)

[Personal Access Tokens](https://en.wikipedia.org/wiki/Personal_access_token) are a kind of _secret_ that is used to control access to resources.   In GitHub, a "Personal Access Token" (PAT) allows a user to access the GitHub API and to automate actions on GitHub using a program. 

On `https://github.ncsu.edu`, create a personal access token through the menu
`settings > Developer settings > Personal access tokens`. Add a new token that expires in 30 days with a limited scope of `repo` access.  

Limiting the scope of the PAT is important, based on the ["Principle of Least Privilege."](https://csrc.nist.gov/glossary/term/least_privilege)  In general, we want to grant only the least amount of privilege required to complete the business task or fulfill the requirements.

Once you copy the token, save it somewhere safe (perhaps in a file in a directory only you can access).

__Do not__, under any circumstances, add any file containing you PAT to your GitHub repo, either as a file or included in the code that runs inside your container. 
Checking in your token will result in a zero for this workshop!  The reason that this penalty is so severe is that in the workplace, you [could get fired for leaking credentials to a public repo (Reddit)](https://www.reddit.com/r/cscareerquestions/comments/135zk4x/fired_for_leaked_credentials_how_do_i_explain_this/).  Also, hackers continually scan GitHub for leaked credentials and [exploit it within minutes](https://www.comparitech.com/blog/information-security/github-honeypot/). 

The NC State GitHub PAT can be used to programmatically access the [NC State GitHub Enterprise REST API](https://docs.github.com/en/enterprise-server@3.9/rest?apiVersion=2022-11-28). 


## 3. Build the container.

On Windows, you can use a program like `powershell` or set up [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install).

On macOS or Linux, start the `terminal` program.  

Navigate to the workshop directory.  From within the workshop directory, run this command to build the workshop and give it the "tag" `ws2` ("workshop-2").

```
docker build . --tag ws2
```

Now that we have the container built, run the container in the "interactive terminal mode," using the `-it` flags .


```
docker run -it ws2
```

As discussed in class, the 'Terminal' is a computational context where you can declare variables, just like within other software programs. 
To see the variables declared in the terminal, run the `env` command so that you can see the environment variables.

```
 env
```
And you should see all the environment variable that have been defined in this container, something like this:
```
HOSTNAME=3e40cb1acf66
SHLVL=1
HOME=/root
TERM=xterm
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PWD=/
```

Now exit this container.

```
exit
```

## 4. Accessing a secret token from inside a container

For our container to run a program that uses the GitHub REST API, we need a way for our program to authenticate to the GitHub API that we have the correct privileges.

It is tempting to copy the token (which is just a string) directly into the container either through the Dockerfile or by adding the token to a file inside the container. However, this "bakes in" the token and anyone who can read the image can extract the token (a security risk).   Baking in a secret (tokens are a kind of secret) into a container is a security risk and a bad idea.

Therefore, we will pass the token into the container from an external file to a local (within-container) environment variable.  Note that this is not the best way to manage secrets (using a program designed for secret management is better yet), but using environment variables is better than hard-coding the token into your program.

Recall that you saved your token somewhere.   Now create a new file named `mytoken.txt` in the workshop folder, and include the following in the file (replace the "<YOUR-GITHUB-TOKEN>" part with your PAT:

```
GITHUB_TOKEN=<YOUR-GITHUB-TOKEN>
```
The file is formatted in an `X=Y` style, with the left-hand side being the name of the environment variable that will appear inside the running container.

Again, the `mytoken.txt` file contains your access token and __should not be added to your repo.__   You can even tell `git` to ignore this file by adding a file to your workshop directory called `.gitignore` that includes the name `mytoken.txt`.

Now, we can use the external file `mytoken.txt` to populate an environment variable in the container with information from outside the container. (`podman` users:  you could also use `podman`'s [secret management tools](https://www.redhat.com/sysadmin/new-podman-secrets-command)).


```
docker run -it --env-file mytoken.txt ws2
```

From within the container, run the `env` command so that you can see the environment variable inside the container terminal environment.

```
env
```

And you should see all the environment variable that have been defined in this container, something like this:

```
GITHUB_TOKEN=<YOUR-GITHUB-TOKEN>
HOSTNAME=3e40cb1acf66
SHLVL=1
HOME=/root
TERM=xterm
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PWD=/
```

Move to the next step :) 

## 5. Modify your container so that it can run Python

The lightweight container with `alpine` linux is designed to only include the [bare-bones](https://en.wiktionary.org/wiki/bare-bones) minimum and does not include a Python interpreter.

Test this by trying to run `python` from within the container.

```
python
```

And you should see:
```
/bin/sh: python: not found
```

We can't find python in the container but we can install it using a [Package Manager (wiki)](https://en.wikipedia.org/wiki/Package_manager).  The Package Manager tool for `alpine` is called the "[Alpine Package Keeper](https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html)", invoked with the command `apk`.  Conceptually, a package manager knows about latest versions of programs (called "packages", because most programs include both files and executable code _"packaged"_ together) that can be installed in the Alpine Linux environment and `apk` can install these programs so we can use them.

First, we need `apk` to update it's internal list of available programs, as follows:

```
apk update
```

and you should see something like:
```
fetch https://dl-cdn.alpinelinux.org/alpine/v3.18/main/aarch64/APKINDEX.tar.gz
fetch https://dl-cdn.alpinelinux.org/alpine/v3.18/community/aarch64/APKINDEX.tar.gz
v3.18.3-108-g8b22d1676dc [https://dl-cdn.alpinelinux.org/alpine/v3.18/main]
v3.18.3-111-gef30a7f5123 [https://dl-cdn.alpinelinux.org/alpine/v3.18/community]
OK: 19938 distinct packages available
```

Notice that `apk` has access to almost 20,000 different packages!

For now, we want to add `python` so we can run python programs, which we do with the following command:

```
apk add python3
```

Now that python is installed, we can run it and test that it's working:

```
python3
Python 3.11.5 (main, Aug 26 2023, 11:59:23) [GCC 12.2.1 20220924] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

Notice that we now have a `python` prompt `>>>` instead of the Alpine Linux prompt `/ #`.

Test that `python3` is working by running a `python` command:

```
>>> print('hello alpine container python world!')
```

and you should see:
```
hello alpine container python world!
```

Let's take this one step further, and read in an environment variable into `python`.   In order for `python` programs to read environment variable, we need to load a `python` library called `os`.

```
import os
```

Now lets use the `os` library to access an environment variable inside the container:

```
print(os.environ.get('FILL-IN-THE-NAME-OF-THIS-ENVIRONMENT-VARIABLE-LOOK-ABOVE'))
```

and you should see:

```
'<YOUR-GITHUB-TOKEN>'
```


## 6. Modify your container so that it can run your program

The container included with this workshop is very simple.  When you look at the included `Dockerfile`, you can see that it only has a few lines:


```
FROM alpine:latest

COPY my-program.py /home
USER root
WORKDIR /home

CMD ["/bin/sh"]
```
^Note that in this `Dockerfile`, each line with a command creates a [new __"layer"__ in the container image](https://docs.docker.com/build/guide/layers/).

In order for this container to run a python program, we need to modify the container so it has python installed.  We know from the previous section that we can add `python` to the container using the `apk command`, but we did that after the container was already running.

Instead, we want to modify the container so that it contains python.  Do do this, we can modify our `Dockerfile` with the command `RUN`.

### Modify the `Dockerfile`

Add this line to the `Dockerfile`, somewhere after `FROM alpine:latest` and before `CMD ["/bin/sh"]`:

```
RUN apk --update-cache add python3
```

Also, __comment__ the line `RUN ["/bin/sh"]` and __uncomment__ this line:

```
CMD python /home/my-program.py
```

Now quit any open containers with `exit`.  Next rebuild the container:

```
docker build (Do you recall the rest of the command to build the container?)
```

After you've rebuilt the container, we can run the program `my-program.py` from within a container like this (notice that we omit the `-it` option flags so that we don't start an interactive terminal):

```
docker run --env-file mytoken.txt ws2
```

and you should see something like:

```
hello world!
<YOUR-GITHUB-TOKEN>
```

Take a screenshot of this an upload it to the form.



## 7. Create a program that runs inside the container that uses the GitHub API

__THIS SECTION AND ITS DELIVERABLE ARE INDIVIDUAL WORK.__

To complete this task, you will likely need to utilize [PyGitHub](https://github.com/PyGithub/PyGithub), especially the [repository commands](https://pygithub.readthedocs.io/en/stable/github_objects/Repository.html), and you might consult the [NC State GitHub Enterprise REST API documentation](https://docs.github.com/en/enterprise-server@3.9/rest?apiVersion=2022-11-28). 

The base URL for the NC State GitHub Enterprise API is:
```
https://github.ncsu.edu/api/v3
```

Your progam shall:

* Run inside an Alpine Linux container.
* Read an environment variable containing an access token.
* Pass the PAT into the container at runtime.
* Use the NC State GitHub REST API to add a branch called `dev` to your forked workshop repo.
* Use the NC State GitHub REST API to add a branch called `release` to your forked workshop repo.
* Be checked in to your forked `CSC-519-WS-2` repo on the `main` branch by the workshop due date.
* Have commented code.
* Gracefully handle the case that the `dev` and `release` branches already exist in the repo.
* (software practice) Be developed using meaningful commit messages (search for "how to write good git commit messages")
* (software practice) Be developed using the software engineering practice of Pull Requests (PRs) (your program doesn't need to create a PR).
* Not include the hard-coded PAT anywhere in the code or the repo.

Your program might include your `unityid` and the name of the repo, and you won't lose points for this, but in general, its better to pass all of this information into the container, either as arguments or environment variables. 

When you are testing your program, you might need to delete your `dev` and `release` branches by hand multiple times -- that is fine.  

To access the GitHub REST API, we recommend [PyGitHub](https://github.com/PyGithub/PyGithub) or [OctoKit JS (Node)](https://github.com/octokit/octokit.js), but you can use other languages if you like.


DO NOT CHECK OR PLACE UNDER VERSION CONTROL ANY FILES CONTAINING YOUR PERSONAL ACCESS TOKEN (will result in a 'zero' for this whole workshop).

Due 23:59 AOE Wednesday, September 6th, Repo synched 

Complete the questions here:
[Google Form file upload](https://forms.gle/iX371JYAgjtqwEQYA)


## That's it :)  Good job.

## Evaluation

This workshop is worth 4 points.

You'll be graded on the following rubric:

| ITEM | POINTS |
|--|--|
| Repo properly forked and configured with teaching staff as collaborators | 0.5 |
| Form Questions | 0.5 |
| Program fulfills requirements | 3 |
| __Auth Token anywhere in Repo__ | __-4__ | 


