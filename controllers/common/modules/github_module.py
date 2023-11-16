from typing import Optional
from github import Github

import docker
import urllib.parse


class GitHubModule:

    async def checkup_repository(self, token: str, repository_name: str):
        """
        ## Checkup repository

        Args:
            credential_id (int): ID of credential
            repository_name (str): Name of repository
        """
        git = Github(token)

        try:
            repo = git.get_repo(repository_name)
            return repo
        except Exception as e:
            return None

    async def create_repository(self, token: str, name: str, /,
                                is_private: bool = True, is_org: bool = False,
                                organization_name: Optional[str] = None):
        """
        ## Creates repository

        Args:
            credential_id (int): ID of credential
            name (str): Name of repository
            is_private (bool, optional): Is repository private. Defaults to True.
            is_org (bool, optional): Is repository in organization. Defaults to False.
        """
        git = Github(token)

        try:
            if is_org:
                repo = git.get_organization(organization_name).create_repo(
                    name, private=is_private)
            else:
                repo = git.get_user().create_repo(name, private=is_private)

            return repo
        except Exception as e:
            return None

    async def clone_repository(self, token: str, repository_name: str, /,
                               is_org: bool = False, organization_name: Optional[str] = None):
        """
        ## Clone repository

        Args:
            token (str): Github auth token
            repository_name (str): Name of repository
            is_org (bool, optional): Is repository in organization. Defaults to False.
        """
        git = Github(token)

        try:
            if is_org:
                repo = git.get_organization(
                    organization_name).get_repo(repository_name)
            else:
                repo = git.get_user().get_repo(repository_name)
            return repo
        except Exception as e:
            return None

    async def clone_and_execute_repository(self, token: str, repository_name: str, /,
                                           is_org: bool = False, organization_name: Optional[str] = None):
        """
        ## Clone repository

        Args:
            token (str): Github auth token
            repository_name (str): Name of repository
            is_org (bool, optional): Is repository in organization. Defaults to False.
        """
        git = Github(token)
        repo = await self.clone_repository(token, repository_name, is_org, organization_name)

        if not repo:
            raise Exception("Repository not found!")

        # Start docker operations
        client = docker.from_env()

        parsed_url = list(urllib.parse.urlparse(repo.clone_url))
        parsed_url[1] = f'{urllib.parse.quote(git.get_user().login)}:{urllib.parse.quote(token)}@{parsed_url[1]}'
        repo_clone_url_with_token = urllib.parse.urlunparse(parsed_url)


        container = client.containers.run(
            'alpine/git',
            name=repo.name,
            command=f"git clone {repo_clone_url_with_token}",
            detach=True
        )
        return container
