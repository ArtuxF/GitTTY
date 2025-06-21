"""
API clients for GitHub and GitLab integration.
Handles authentication and repository operations.
"""

import requests
import json
from typing import List, Dict, Optional

try:
    from rich.console import Console
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class GitAPIError(Exception):
    """Custom exception for Git API related errors."""
    pass


class BaseGitClient:
    """Base class for Git service API clients."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update(self._get_auth_headers())
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers. To be implemented by subclasses."""
        raise NotImplementedError
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a request with error handling."""
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            
            if response.status_code == 401:
                raise GitAPIError("Authentication failed. Please check your token.")
            elif response.status_code == 403:
                if 'rate limit' in response.text.lower():
                    raise GitAPIError("Rate limit exceeded. Please try again later.")
                else:
                    raise GitAPIError("Access forbidden. Check your token permissions.")
            elif response.status_code == 404:
                raise GitAPIError("Resource not found.")
            elif not response.ok:
                raise GitAPIError(f"API request failed with status {response.status_code}")
            
            return response
        except requests.exceptions.ConnectionError:
            raise GitAPIError("Network connection error. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise GitAPIError("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise GitAPIError(f"Request failed: {str(e)}")


class GitHubClient(BaseGitClient):
    """GitHub API client."""
    
    BASE_URL = "https://api.github.com"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def test_connection(self) -> Dict[str, str]:
        """Test the connection and get user info."""
        response = self._make_request("GET", f"{self.BASE_URL}/user")
        user_data = response.json()
        return {
            "username": user_data.get("login"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "public_repos": user_data.get("public_repos"),
            "private_repos": user_data.get("total_private_repos", 0)
        }
    
    def get_repositories(self, per_page: int = 30, repo_type: str = "all") -> List[Dict]:
        """Get user repositories."""
        params = {
            "per_page": per_page,
            "type": repo_type,  # all, owner, member
            "sort": "updated",
            "direction": "desc"
        }
        
        response = self._make_request("GET", f"{self.BASE_URL}/user/repos", params=params)
        repos = response.json()
        
        return [
            {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "clone_url_https": repo["clone_url"],
                "clone_url_ssh": repo["ssh_url"],
                "private": repo["private"],
                "language": repo.get("language"),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "updated_at": repo["updated_at"],
                "default_branch": repo["default_branch"]
            }
            for repo in repos
        ]
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """Get detailed information about a specific repository."""
        response = self._make_request("GET", f"{self.BASE_URL}/repos/{owner}/{repo}")
        repo_data = response.json()
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description", ""),
            "clone_url_https": repo_data["clone_url"],
            "clone_url_ssh": repo_data["ssh_url"],
            "private": repo_data["private"],
            "language": repo_data.get("language"),
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "size": repo_data["size"],
            "default_branch": repo_data["default_branch"],
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"]
        }


class GitLabClient(BaseGitClient):
    """GitLab API client."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        self.base_url = base_url.rstrip('/')
        super().__init__(token)
    
    @property
    def api_url(self):
        return f"{self.base_url}/api/v4"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict[str, str]:
        """Test the connection and get user info."""
        response = self._make_request("GET", f"{self.api_url}/user")
        user_data = response.json()
        return {
            "username": user_data.get("username"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "public_repos": "N/A",  # GitLab doesn't provide this directly
            "private_repos": "N/A"
        }
    
    def get_repositories(self, per_page: int = 30, owned: bool = True) -> List[Dict]:
        """Get user repositories."""
        params = {
            "per_page": per_page,
            "owned": str(owned).lower(),
            "order_by": "updated_at",
            "sort": "desc"
        }
        
        response = self._make_request("GET", f"{self.api_url}/projects", params=params)
        repos = response.json()
        
        return [
            {
                "name": repo["name"],
                "full_name": repo["path_with_namespace"],
                "description": repo.get("description", ""),
                "clone_url_https": repo["http_url_to_repo"],
                "clone_url_ssh": repo["ssh_url_to_repo"],
                "private": repo.get("visibility", "private") == "private",
                "language": None,  # GitLab doesn't provide primary language in list
                "stars": repo.get("star_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": repo["last_activity_at"],
                "default_branch": repo.get("default_branch", "main")
            }
            for repo in repos
        ]
    
    def get_repository_info(self, project_id: str) -> Dict:
        """Get detailed information about a specific repository."""
        response = self._make_request("GET", f"{self.api_url}/projects/{project_id}")
        repo_data = response.json()
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["path_with_namespace"],
            "description": repo_data.get("description", ""),
            "clone_url_https": repo_data["http_url_to_repo"],
            "clone_url_ssh": repo_data["ssh_url_to_repo"],
            "private": repo_data.get("visibility", "private") == "private",
            "language": None,
            "stars": repo_data.get("star_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "size": None,  # GitLab doesn't provide size directly
            "default_branch": repo_data.get("default_branch", "main"),
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["last_activity_at"]
        }


def create_client(service: str, token: str, gitlab_url: str = "https://gitlab.com") -> BaseGitClient:
    """Factory function to create appropriate API client."""
    if service.lower() == "github":
        return GitHubClient(token)
    elif service.lower() == "gitlab":
        return GitLabClient(token, gitlab_url)
    else:
        raise ValueError(f"Unsupported service: {service}")


def test_token(service: str, token: str, gitlab_url: str = "https://gitlab.com") -> tuple[bool, str, Dict]:
    """Test if a token is valid for the given service."""
    try:
        client = create_client(service, token, gitlab_url)
        user_info = client.test_connection()
        return True, "Connection successful", user_info
    except GitAPIError as e:
        return False, str(e), {}
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", {}
