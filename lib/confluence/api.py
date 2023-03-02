import json
import mimetypes
import os
import sys

import requests

from lib.confluence.page import Page


def get_page_api(base_url, space_key, title, pat, **_):
    url = f"{base_url}/rest/api/content?title={title}&spaceKey={space_key}&expand=version,ancestors"

    headers = {"content-type": "application/json", "Authorization": f"Bearer {pat}"}
    response = requests.get(url, headers=headers)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err)
        print(f"base url: {base_url}")
        print(f"space key: {space_key}")
        sys.exit(1)

    data = response.json()

    if results := data["results"]:
        id = results[0]["id"]
        version_num = results[0]["version"]["number"]
        link = f"{base_url}{results[0]['_links']['webui']}"

        return Page(id, version_num, link)

    return None


def create_page_api(base_url, space_key, ancestor_id, title, body, pat, **_):
    url = f"{base_url}/rest/api/content"

    headers = {"content-type": "application/json", "Authorization": f"Bearer {pat}"}

    page_json = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": body, "representation": "storage"}},
        "ancestors": [{"id": ancestor_id}],
    }

    response = requests.post(url, data=json.dumps(page_json), headers=headers)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err)
        print(f"base url: {base_url}")
        print(f"space key: {space_key}")
        sys.exit(1)

    if response.status_code == 200:
        data = response.json()
        space_name = data["space"]["name"]
        id = data["id"]
        version = data["version"]["number"]
        link = f"{base_url}/pages/viewpage.action?pageId={id}"

        print(f"page created in {space_name} with id: {id}")
        print(f"url: {link}")
        return Page(id, version, link)
    else:
        print(f"failed to create page. {response}")
        sys.exit(1)


def update_page_api(
    base_url, space_key, ancestor_id, title, id, body, version, pat, **_
):
    url = f"{base_url}/rest/api/content/{id}"
    headers = {"content-type": "application/json", "Authorization": f"Bearer {pat}"}
    page_json = {
        "id": id,
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": body, "representation": "storage"}},
        "version": {"number": version, "minorEdit": True},
        "ancestors": [{"id": ancestor_id}],
    }
    response = requests.put(url, data=json.dumps(page_json), headers=headers)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err)
        print(f"base url: {base_url}")
        print(f"space key: {space_key}")
        sys.exit(1)

    if response.status_code == 200:
        data = response.json()
        space_name = data["space"]["name"]
        id = data["id"]
        version = data["version"]["number"]
        link = f"{base_url}/pages/viewpage.action?pageId={id}"

        print(f"page updated in {space_name} with id: {id}")
        print(f"url: {link}")
        return Page(id, version, link)
    else:
        print(f"failed to create page. {response}")
        sys.exit(1)


def upsert_attachment(base_url, id, file_path, comment, pat, **_):
    content_type = mimetypes.guess_type(file_path)[0]
    file_name = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        print(f"{file_path} is not found")
        sys.exit(1)

    with open(file_path, "rb") as f:
        file_to_upload = {
            "comment": comment,
            "file": (file_name, f, content_type, {"Expires": "0"}),
        }
        if attachment_id := get_attachment(base_url, id, file_path, pat):
            url = f"{base_url}/rest/api/content/{id}/child/attachment/{attachment_id}/data"
        else:
            url = f"{base_url}/rest/api/content/{id}/child/attachment"
        headers = {"Authorization": f"Bearer {pat}", "X-Atlassian-Token": "no-check"}
        response = requests.post(url, files=file_to_upload, headers=headers)

        try:
            response.raise_for_status()
        except requests.RequestException as err:
            print(err)
            print(f"base url: {base_url}")
            print(f"id: {id}")
            sys.exit(1)


def get_attachment(base_url, id, file_path, pat):
    file_name = os.path.basename(file_path)
    url = f"{base_url}/rest/api/content/{id}/child/attachment?filename={file_name}"

    headers = {"content-type": "application/json", "Authorization": f"Bearer {pat}"}
    response = requests.get(url, headers=headers)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err)
        print(f"base url: {base_url}")
        sys.exit(1)

    data = response.json()
    if attachments := data["results"]:
        attachment_id = attachments[0]["id"]
        return attachment_id
    else:
        return None


def add_label(base_url, id, label, pat, **_):
    url = f"{base_url}/rest/api/content/{id}/label"
    headers = {"Authorization": f"Bearer {pat}", "X-Atlassian-Token": "no-check"}
    label_json = {"prefix": "global", "name": label}

    response = requests.post(url, data=json.dumps(label_json), headers=headers)

    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err)
        print(response.content)
        print(f"base url: {base_url}")
        print(f"id: {id}")
        sys.exit(1)
