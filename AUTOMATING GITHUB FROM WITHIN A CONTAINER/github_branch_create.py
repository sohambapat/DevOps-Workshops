import os
import requests

#read GitHub PAT from env
github_token = os.getenv("GITHUB_TOKEN")

#define the repository and branch names
repository = "sbapat2/CSC-519-WS-2"
base_url = "https://github.ncsu.edu/api/v3/repos/"

def get_sha_for_branch(branch_name):
    url = f"{base_url}{repository}/branches/{branch_name}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        branch_info = response.json()
        return branch_info["commit"]["sha"]
    else:
        print(f"Failed to retrieve SHA for branch '{branch_name}'.")
        print(response.status_code, response.text)
        return None

def create_branch(branch_name, base_branch):
    base_sha = get_sha_for_branch(base_branch)
    
    if base_sha:
        url = f"{base_url}{repository}/git/refs"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check if the branch already exists
        existing_branch = f"refs/heads/{branch_name}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            branches = response.json()
            for branch in branches:
                if branch["ref"] == existing_branch:
                    print(f"The branch '{branch_name}' already exists.")
                    return
        
        # Create the new branch
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Branch '{branch_name}' created successfully.")
        else:
            print(f"Failed to create branch '{branch_name}'.")
            print(response.status_code, response.text)

if __name__ == "__main__":
    # Define the branch names and base branch
    dev_branch_name = "dev"
    release_branch_name = "release"
    base_branch = "main"
    
    # Create the dev branch
    create_branch(dev_branch_name, base_branch)
    
    # Create the release branch
    create_branch(release_branch_name, base_branch)
