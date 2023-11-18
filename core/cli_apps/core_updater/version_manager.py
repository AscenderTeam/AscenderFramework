from github import Github, Repository, GitRelease
import requests

from settings import BASE_PATH


class VersionManager:
    def __init__(self) -> None:
        self.git = Github()
    
    def get_repository(self) -> Repository.Repository:
        return self.git.get_repo("AscenderTeam/AscenderFramework")
    
    def get_latest_release(self) -> GitRelease.GitRelease:
        return self.get_repository().get_latest_release()
    
    def check_for_update(self) -> bool:
        return self.get_latest_release().tag_name != "v0.0.1"
    
    def download_release(self, release: GitRelease.GitRelease):
        with requests.get(release.upload_url, stream=True) as r:
            r.raise_for_status()
            with open(f"{BASE_PATH}/.update_version", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

