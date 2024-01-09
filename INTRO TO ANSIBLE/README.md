

#  INTRO TO ANSIBLE


## LEARNING GOALS

In this workshop, the goal is for you to learn about how manage a configuration ("Configuration Management") of remote resources using [Ansible](https://en.wikipedia.org/wiki/Ansible_(software)).  We'll look at the main elements of ansible-playbooks and how to use an ansible playbook to install and configure software on a remote machine.



## Assumptions:  
* [`docker` installed](https://docs.docker.com/get-docker/)

## 0. Fork this workshop

Firstly, create a copy of `CSC-519-WS-4` by [forking it](https://en.wikipedia.org/wiki/Fork_(software_development)) to your user account.  Do not change the name.

NOTE: Add the teaching staff as "admin" level collaborators (unity IDs: `mrahman` and `jwore`) under "Settings > Collaborators and Teams."

Check out your fork of `CSC-519-WS-4` locally so you can work with it.


## 1. Provision a Cloud Instance (the "Inventory")

As discussed in class, Ansible is a configuration managmeent tool. In this workshop, we're going to use Ansible to configure a remote machine.
Therefore, we need to set up a machine to configure.   

We want to set up a particular kind of machine---an __Ubuntu 22.04 LTS__ cloud instane.  You can do the following:

* __Recommended.__ Set up an  instance using NC State's [Virtual Computing Lab by clicking the "Reservations" button.](https://vcl.ncsu.edu/).   Create a "basic" reservation with a duration of up to 10 hours (you can also just do less (2 hours) if you know that you're just going to work on this workshop during class time).  After 10 hours your reservation will expire and you'll have to create a new one, but this is OK because the whole point of this workshop is for you to create an Ansible script that sets up the managed machine.   Once you make the reservation, it will be "pending" for a few minutes until the VM is provisioned.  Once the provisioning has completed, the "Connect" button will provide instructions on how to SSH into the managed machine.
* Sign up for a [60-day free trial at DigitalOcean](https://www.digitalocean.com/try/free-trial-offer).   When you sign up, you get $200 credit for 60 days but it will ask for your credit card as backup. It won’t charge you anything until you use up the credit or if your credit expires. And at that point it’s still really cheap, starting at $0.00595/hr for a droplet (a virtual machine).
* Use a differet cloud provider to provision an Ubuntu 22.04 LTS instance.

Regardless of which method you choose from the list above, by the end of this step, you'll need:
* The `ip-address` of the remote machine  (either something like `192.168.1.42` for an [IPv4](https://en.wikipedia.org/wiki/Internet_Protocol_version_4) address and `2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF` for an [IPv6](https://en.wikipedia.org/wiki/IPv6) address).
* username for the remote machine
* login credentials for the remote machine (for VCL, this is your Unity-Id password)


## 2. Generate SSH keys

This step is about the "[secure shell](https://en.wikipedia.org/wiki/Secure_Shell)" more commonly known as `ssh` ("ESS-ESS-AECH").

(You can skip this step if you already have an `id_rsa.pub` file generated from `ssh-keygen.`  You can test this if you have an `ssh` key from the terminal with this command: `ls ~/.ssh/id_rsa.pub`. 

In order for your machine to act as the "Ansible Control Node," you need to be able to connect over an encrypted data channel to your remote machine (the "Inventory," as Ansible calls it).

Here are Step-by-step guides for creating your `ssh` key, which will be stored in `~/.ssh/id_rsa.pub`:

* [Windows](https://github.ncsu.edu/software-engineering-for-robotics/course/wiki/Getting-Started-with-Command-line-Git#generate-ssh-key-on-windows-10)
* [Setting up SSH keys on MacOS or Ubuntu](https://github.ncsu.edu/software-engineering-for-robotics/course/wiki/Getting-Started-with-Command-line-Git#generate-ssh-key-on-osx-or-ubuntu)

In either case, confirm from a terminal that you now have an `id_rsa.pub` from the terminal:

```
ls ~/.ssh/id_rsa.pub
```
And you should see something like:
```
/Users/YOUR-USER-NAME/.ssh/id_rsa.pub
```

Ok good!  Let's test it :) 


## 3. Test the connection to your remote instance.

From a terminal, try the following:
```
ssh <YOUR-UNITY-ID-OR-USERNAME>@<YOUR-REMOTE-MACHINE-IP-ADDRESS>
```
and the first time you `ssh` into a new machine you should see something like:
```
The authenticity of host '152.7.179.25 (152.7.179.25)' can't be established.
ECDSA key fingerprint is SHA256:qwgNS1vk9dz7d8ix1QZAwzl4idMvATB+TH9RvqQkmjs.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
Answer yes by typing `yes` and hitting the return key.  This only happens the first time you connect to a new machine over `ssh`. Now you should see something like:
```
<YOUR-UNITY-ID-OR-USERNAME>@152.7.179.25's password:
```
Enter your password (for VCL users, this will be your UNITY-ID password).

If this worked, you'll should see a terminal command prompt, like this:
```
<YOUR-UNITY-ID-OR-USERNAME>@vclvm179-25:~$
```
Progress! Now we've tested the `ssh` connection to the remote machine.  We can exit the connection to the remote machine with the `exit` command, which closes this `ssh` terminal session and closes the conenction.
```
exit
```

Now that we know the `ssh` connection works, we need to make it work __without entering a password__ so that Ansible can use `ssh` to run commands on the machine without a password.


## 4. Set up the remote machine for `ssh` access without a password.

Now we need to configure your remote machine so that you can `ssh` into it without being prompted for a password.

We can do this the long way or the short way.   

### The long way (more detail, recommended)

1. Copy your `id_rsa.pub` to the remote machine, using the `scp` command(`scp` stands for "secure copy", which uses `ssh` to securely copy a file from one machine to another) , like this `scp ~/.ssh/id_rsa.pub <YOUR-UNITY-ID-OR-USERNAME>@<YOUR-REMOTE-MACHINE-IP-ADDRESS>:` (NOTE the trailing `:` at the end of the command -- this specifies the destination of the file to the default user directory `~`).  
2. `ssh` into the remote machine again.
3. Append the contents of your `id_rsa.pub` to the `~/.ssh/authorized_keys` file, like this:  `cat id_rsa.pub >> ~/.ssh/authorized_keys`, where `>>` appends the output of the `cat` command to a file.  The `cat` command stands for "concatenate."
4. Delete your `id_rsa.pub` file from the remote machine: `rm id_rsa.pub` 
5. Exit the remote connection with `exit`.

### The short way (one line)

This one-line command specifies the identity file `~/.ssh/id_rsa.pub` using the `-i` flag on the command.

```
ssh-copy-id -i ~/.ssh/id_rsa.pub <YOUR-UNITY-ID-OR-USERNAME>@<YOUR-REMOTE-MACHINE-IP-ADDRESS>
```

__After either the long way or the short way__, now we can test that we can access the remote machine without a password in the next step.


## 5. Test ssh connection to cloud instance

Try connecting to your remote machine again using a terminal on your local machine:

```
ssh <YOUR-UNITY-ID-OR-USERNAME>@<YOUR-REMOTE-MACHINE-IP-ADDRESS>
```
And __without__ having to enter your password, you should see something like:
```
<YOUR-UNITY-ID-OR-USERNAME>@vclvm179-25:~$
```
Hooray! (and Whew) 

Now we can get to the Ansible stuff :) 


## 6. Set up the Ansible `hosts.yaml` file

From the terminal, navigate the workshop directory.  Now create a file called `hosts.yaml` and add the following lines:
```
[myserver]
<YOUR-REMOTE-MACHINE-IP-ADDRESS> ansible_user=<YOUR-UNITY-ID-OR-USERNAME> 
```

In the lines above, we're creating a file that Ansible can use to find the remote machines on which to do the management.
The `ansible_user` part tells Ansible how construct the `ssh` command it uses internally to access the remote machine.
Notice that we're specifying the username that we want Ansible to use when connecting to the remote machine.
To see more about creating and configuring multiple hosts, see [the Ansible docs page on inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html).

Depending on your remote environment, you might also need to append the following to the `hosts.yaml` on the same line as the ip address: `ansible_python_interpreter=/usr/bin/python3`

Now that we have a host, we can configure that host with a playbook in the next step.

## 7. Set up the Ansible playbook

Create a file in your workshop directory called `deploy-webserver.yaml`.    

Add the following lines:

```
---
- name: Demo playbook
  hosts: myserver
  become: yes
  become_method: sudo
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: latest
        
    - name: Start nginx service
      service:
        name: nginx
        enabled: true
        state: started
```
Look at each command in this playbook.  Notice that it currently has 2 tasks:  `Install nginx` and `Start nginx service`. The first task (`Install nginx`) uses the Ubuntu package manager `apt`, as can be seen on the first line under the name `Install nginx`, and we're asking to install the latest version.

### Latest version or specify a version?
Using the latest version has advantages and disadvantages. The advantage is that we'll have the newest version (or the newest version that is available through `apt`, which is not the same thing).  The disadvantage is that the newest version might in the future introduce breaking changes to interface, so that is a risk.  If we chose to specify the version of `nginx` we wanted (instead of the latest), then we'd know which version we have (which is good) but over time, the version specified in our Ansible file will become old, which might be bad.   There is no perfect answer here, only tradeoffs.


Now that we have the `nginx` webserver installed, let's have Ansible create an `html` file (add this to your playbook):

```
    - name: Create a custom index.html file
      copy:
        dest: /var/www/html/index.html
        content: |
          <h1>Hello CSC-519 World!</h1>
```

Note that __"inlining" the content in our Ansible file is not normal and is for demonstration purposes only__ and it would be better to copy or clone file a program from another source.  The principle here is not to include one language (`html/javascript`) inside another language (`ansible`).

One more thing before we try running this playbook--If you're running on a `vcl` machine, add the following to allow inbound traffic to the VCL machine on port `80`, the default `http` traffic port:

```
    - name: Expose port 80 with iptables
      shell: 
        "sudo iptables -I INPUT -p tcp -m tcp --dport 80 -j ACCEPT"
```

That's it -- now we're ready to run the playbook!


## 8. Run the Ansible container

On Windows, you can use a program like `powershell` or set up [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install).

On macOS or Linux, start the `terminal` program.  

Navigate to the workshop directory.  From within the workshop directory, run this command to build the workshop and give it the "tag" `ws2` ("workshop-2").

```
docker build . --tag ws4
```

Now that we have the container built, run the container in the "interactive terminal mode," using the `-it` flags .


To run `ansible-playbook` from within a Docker container, we're going to need to mount 2 volumes ([recall the `-v` option from Workshop-1?](https://github.ncsu.edu/CSC-519/workshop-1/blob/main/README.md)):
* the local workshop directory of your workshop should be mounted as `/ws4` in the container (<YOUR-DOCKER-VOLUME-MOUNT-COMMAND-1> below)
* your local `.ssh` directory should be mounted as `/root/.ssh` in the container (<YOUR-DOCKER-VOLUME-MOUNT-COMMAND-2> below)

```
docker run -it <YOUR-DOCKER-VOLUME-MOUNT-COMMAND-1> <YOUR-DOCKER-VOLUME-MOUNT-COMMAND-2> ws4
```

## 9. Run the playbook

So that we're clear, you're running the Ansible control node locally in a Docker container, with Docker configured to access local resources like `~/.ssh` and the contents of your workshop directory that has the `hosts` and `deploy-webserver.yaml` playbook.


NOTE:  __This command is intentionally wrong in 3 ways__, you'll need to try it to figure out the correct syntax:
```
ansible -i ./hosts deploy-webserver.yml
```

Once you get this working, you should see ansible's output from running the playbook.


Now, run the playbook again for the `deploy-webserver.yaml`. Notice that it is faster this time, and that the result should be the same.  Running an ansible playbook multiple times should result in the same end state.


## 10. Test the web server.

Open a web browser and go to this URL: `http://<YOUR-REMOTE-MACHINE-IP-ADDRESS>`.  

You should see something like:
```
Hello CSC-519 World!
```

Congratulations, you've configured a remote machine with Ansible and started a web server :)



## 11. Create a ansible playbook that runs a `NodeJS` program

__THIS SECTION AND ITS DELIVERABLE ARE INDIVIDUAL WORK.__

This step is asking you to pick up a little `nodejs` if you have not done so already, and I realize that we have not discussed `nodejs` in class.  So this is might be a little bit of "throwing someone into a swimming pool."  But in the era of `ChatGPT,` it might not be a large barrier for you to create basic `nodejs` code.

Your Ansible playbook shall:

* Install and start the latest version of an `nginx` webserver (given above)
* Install `nodejs`
* Install a `nodejs` app __that you create__.  You may use generative tools like ChatGPT as a starting point.  You can either keep your app files in your forked repository or pull from another repo.
* Install `nodejs` `npm` packages required to run your web app (if any).
* Run a `nodejs` app (a web server) on port `80` that responds with at least "Hello CSC-519 World!" (see this [NodeJS getting started guide](https://nodejs.org/en/docs/guides/getting-started-guide))
* Use Ansbile to test that your web server is up ([see this example](https://blog.devops.dev/ansible-how-to-check-if-an-http-web-server-or-api-is-accessible-or-not-b4a98a6c748d))
* BONUS: 0.5 bonus points are availble if your playbook creates a `SQL` database (any SQL database will do) *and* your `nodejs` app retrieves data from that DB and presents it on the landing page of your app. 



Due 23:59 AOE Thursday, September 21st, Repo synched. 

Complete the questions here:
[Google Form file upload](https://forms.gle/LKjM5QAL6GvT1MFK9)


## That's it :)  Good job.

## Evaluation

This workshop is worth 4 points.

You'll be graded on the following rubric:

| ITEM | POINTS |
|--|--|
| Repo properly forked and configured with teaching staff as collaborators | 0.25 |
| Form question | 0.25 |
| Program fulfills requirements | 3.5 |
| Form not submitted | -2.0 |
| Database Connection -- see above.| __+0.5 BONUS__|
| `ssh` keys or any tokens checked in on your repo in any format | __-4.0__ |

