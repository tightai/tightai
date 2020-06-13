# AUTOGENERATED! DO NOT EDIT! File to edit: 01_projects.ipynb (unless otherwise specified).

__all__ = ['VersionManager', 'Version', 'ProjectManager', 'Project']

# Cell
import time
import urllib.parse
import webbrowser
from pathlib import Path
from slugify import slugify
from tightai import exceptions
from .exceptions import ArgumentsRequired
from .lookup import Lookup
from .base import BaseObject, base_tightignore
from .conf import CLI_ENDPOINT
from .downloaders import DownloadVersion
from .user import UserObject
from .upload import Uploader
from .utils import sort_by_key, print_dict

# Cell
class VersionManager(Lookup, BaseObject):
    api = CLI_ENDPOINT
    version = None
    project_id = None

    def __str__(self):
        return f"<VersionManager>"

    def __repr__(self):
        return self.__str__()

    def create(self, project_id=None, raw=False, **kwargs):
        '''
        Creates an empty project version.
        '''
        if project_id == None:
            raise ArgumentsRequired("project_id")
        r = self.http_post(f"/projects/{project_id}/versions/", data=kwargs)
        if raw:
            return r
        self.handle_invalid_lookup(r, expected_status_code=201)
        return Version(**r.json())

    def get(self, version=None, project_id=None, raw=False):
        if project_id == None or version == None:
            raise ArgumentsRequired("version", "project_id")
        r = self.http_get(f"/projects/{project_id}/versions/{version}")
        if raw:
            return r
        self.handle_invalid_lookup(r, expected_status_code=200)
        return Version(**r.json())

    def latest(self, project_id=None, none_on_404=False, deployed=False):
        if project_id == None:
            raise ArgumentsRequired("project_id")
        deployed_str = f"{deployed}".lower()
        r = self.http_get(f"/projects/{project_id}/latest/?deployed={deployed_str}")
        if deployed == True:
            none_on_404 = True
        if r.status_code == 404 and none_on_404:
            return None
        self.handle_invalid_lookup(r, expected_status_code=200)
        return Version(**r.json())

    def all(self, project_id=None, **kwargs):
        if project_id == None:
            raise ArgumentsRequired("project_id")
        endpoint = f"/projects/{project_id}/versions/"
        if len(kwargs.keys()):
            query_string = urllib.parse.urlencode(kwargs)
            endpoint = f"{endpoint}?{query_string}"
        r = self.http_get(endpoint)
        self.handle_invalid_lookup(r, expected_status_code=200)
        return [Version(**x) for x in r.json()['results']]

    def get_or_create(self, **kwargs):
        created = False
        version = None
        try:
            existing_r = self.get(**kwargs)
        except:
            existing_r = None
        if existing_r != None:
            return existing_r, created
        new_v = self.create(**kwargs)
        created = True
        return new_v, created

# Cell
class Version(Lookup, BaseObject):
    '''
    An individual release of any given project.
    '''
    version = None
    project_id = None
    trigger_options = ['status', 'build', 'build_and_deploy', 'deploy', 'destroy']
    display_options = ['project_id', 'version', 'description', 'url', 'deployed',
                       'deployed_timestamp', 'destroyed', 'destroyed_timestamp', 'updated', 'timestamp']

    def __str__(self):
        return f"<Version {self.version} ({self.project_id})>"

    objects = VersionManager()

    def build(self):
        return self.update_trigger(option='build')

    def delete(self):
        confirmation_code = f"{self.project_id}-v{self.version}"
        response = input(f"Deleting is cannot be reversed. Please confirm by typing:\n\n{confirmation_code}\n\n")
        if f"{response}".strip() != confirmation_code:
            print(f"\nDelete failed. {response} did not match {confirmation_code} exactly.")
            return
        r = self.http_delete(f"/projects/{self.project_id}/versions/{self.version}")
        self.handle_invalid_lookup(r, expected_status_code=204)
        setattr(self, 'deleted', True)
        return r

    def summary(self, verbose=0):
        data = {
            "version": self.version,
            "project_id": self.project_id,
            "url": self.url,
            "deployed": self.deployed,
            "updated": self.updated
        }
        if verbose == 1:
            print_dict(data)
        return data

    def deploy(self):
        raise Exception("Use `.push(local_path)` to deploy instead.")

    def destroy(self):
        return self.update_trigger(option='destroy')

    def upload(self, path=".", verbose=True):
        src_path = Path(path).resolve()
        tightai_ignore = src_path / ".tightignore"
        if not tightai_ignore.exists():
            print("No .tightignore found. Creating default.")
            with open(str(tightai_ignore), "w") as f:
                f.writelines(base_tightignore)
        uploader = Uploader(path=path, project_id=self.project_id, version=self.version)
        uploaded_count = uploader.upload(verbose=verbose)
        return uploaded_count

    def status(self, wait=True, display=True):
        endpoint = f"/projects/{self.project_id}/versions/{self.version}/status/"
        r = self.http_post(endpoint, data={})
        if r.status_code != 200:
            raise Exception("Could not find status at this time.")
        r_data = r.json()
        for k,v in r_data.items():
            setattr(self, k, v)
        verbose = 1
        if display == False:
            verbose = 0
        return self.details(verbose=verbose)

    def refresh(self):
        version = self.objects.get(version=self.version, project_id=self.project_id)
        for k,v in version.__dict__.items():
            setattr(self, k, v)
        return version.details()

    def push(self, path, check_status=True):
        project_id = self.project_id
        version = self.version
        uploaded_count = self.upload(path, verbose=True)
        if uploaded_count == 0:
            print(f"Uploaded 0 files. Continuing")
        print("Deploying...")
        deploy_r = self.update_trigger(option='build_and_deploy')
        if deploy_r.status_code != 200:
            raise Exception("Project not deployed. Please try again.")
        if not check_status:
            print(f"{project_id} {version} pushed. Use `.status()` to check deployment status.")
            return None
        details = self.status(wait=True)
        url = details.get('url')
        if not url:
            print("URL is not ready yet. Use `.status()` to check deployment status.")
            return None
        setattr(self, 'url', url)
        return url

    def download(self, path, overwrite=False):
        dest = Path(path).resolve()
        project_id = self.project_id
        version = self.version
        dl = DownloadVersion(path=path, project_id=project_id, version=version)
        dl.download(overwrite=overwrite)

    def update_trigger(self, option='status'):
        if option not in self.trigger_options:
            print(f"{option} is invalid. Please try again.")
            option = 'status'
        data = {
            'trigger_active': True,
            'trigger': f"{option}",
        }
        r = self.http_put(f"/projects/{self.project_id}/versions/{self.version}", data=data)
        self.handle_invalid_lookup(r, expected_status_code=200)
        self.update_from_response(r)
        return r

    def update_from_response(self, response, display=False):
        for k, v in response.json().items():
            if display:
                print(f"{k}")
            current_v = getattr(self, k)
            if v != None and current_v != v:
                setattr(self, k, v)
        return

    def open(self):
        details = self.details()
        url = details.get("url")
        if url == None or details['deployed'] == False:
            raise Exception("This version has not been deployed yet. Push a deployment or refresh version status.")
        return webbrowser.open(url)


# Cell
class ProjectManager(Lookup, BaseObject):
    api = CLI_ENDPOINT
    version = None

    def __str__(self):
        return f"<ProjectManager>"

    def __repr__(self):
        return self.__str__()

    def create(self, **kwargs):
        r = self.http_post(f"/projects/", data=kwargs)
        self.handle_invalid_lookup(r, expected_status_code=201)
        return Project(**r.json())

    def get(self, project_id=None):
        if project_id == None:
            raise ArgumentsRequired("project_id")
        r = self.http_get(f"/projects/{project_id}/")
        self.handle_invalid_lookup(r, expected_status_code=200)
        return Project(**r.json())

    def all(self, **kwargs):
        endpoint = f"/projects/"
        if len(kwargs.keys()):
            query_string = urllib.parse.urlencode(kwargs)
            endpoint = f"{endpoint}?{query_string}"
        r = self.http_get(endpoint)
        self.handle_invalid_lookup(r, expected_status_code=200)
        return [Project(**x) for x in r.json()['results']]

    def get_or_create(self, **kwargs):
        created = False
        existing_r = self.get()
        if existing_r.status_code == 200:
            return existing_r, created
        new_r = self.create(**kwargs)
        self.handle_invalid_lookup(new_r, expected_status_code=201)
        created = True
        return new_r, created


class Project(Lookup, BaseObject):
    project_id = None
    display_options = ['name', 'id', 'description',
                       'updated', 'timestamp', 'versions_metadata', 'versions_urls']

    def __str__(self):
        return f"<Project {self.id}>"

    def summary(self, verbose=0):
        data = {
            "name": self.name,
            "project_id": self.project_id,
            "versions_summary": {
                "deployed": self.versions_metadata.get('deployed_count'),
                "urls": self.versions_urls,
            },
            "updated": self.updated
        }
        if verbose == 1:
            print_dict(data)
        return data

    @property
    def project_id(self):
        return self.id

    objects = ProjectManager()

    def create_version(self, version=None):
        if version == None:
            raise ArgumentsRequired("version")
        version, _ = Version.objects.get_or_create(project_id=self.project_id, version=version)
        return version

    def get_version(self, version=None):
        if version == None:
            raise ArgumentsRequired("version")
        version, _ = Version.objects.get_or_create(project_id=self.project_id, version=version)
        return version

    def delete(self):
        print("You can only delete projects in the tight.ai console right now.")

    def get_versions(self):
        versions = Version.objects.all(project_id=self.project_id)
        return versions

    def latest(self, deployed=False):
        return Version.objects.latest(project_id=self.project_id, deployed=deployed)