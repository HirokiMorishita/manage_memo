#!/usr/bin/env python
import argparse
import os
import re
import sys

import frontmatter

from lib.confluence import api, convert

parser = argparse.ArgumentParser()
parser.add_argument(
    "file_path", help="path of the markdown file to convert and upload."
)
parser.add_argument("pat_file_path", help="path of confluence paersonal access token.")


def main(args):
    markdown_data = read_markdown(args.file_path)

    pat = read_pat(args.pat_file_path)
    if id := markdown_data.metadata.get("id"):
        html = convert.to_html(markdown_data.content, id)
        upload_image(args.file_path, markdown_data.content, markdown_data.metadata, pat)
        _, updated_metadata = update_page(html, markdown_data.metadata, pat)
    else:
        html = convert.to_html(markdown_data.content)
        page, updated_metadata = create_page(html, markdown_data.metadata, pat)
        html = convert.to_html(markdown_data.content, page.id)
        upload_image(args.file_path, markdown_data.content, updated_metadata, pat)
        _, updated_metadata = update_page(html, updated_metadata, pat)
    markdown_data.metadata = updated_metadata
    save_markdown(args.file_path, markdown_data)
    if "label" in markdown_data.metadata:
        api.add_label(pat=pat, **updated_metadata)


def create_page(html, metadata, pat):
    if page := api.get_page_api(pat=pat, **(metadata)):
        print(f"{metadata} already exist in confluence")
        sys.exit(1)
    else:
        params = metadata | {"body": html, "pat": pat}
        page = api.create_page_api(**params)
        updated_metadata = metadata | vars(page)
        return page, updated_metadata


def update_page(html, metadata, pat):
    if page := api.get_page_api(pat=pat, **(metadata)):
        assert metadata.get("id") == page.id
        assert metadata.get("version") == page.version
        version = page.version + 1
        params = metadata | {"body": html, "version": version, "pat": pat}
        page = api.update_page_api(**params)
        updated_metadata = metadata | vars(page)
        return page, updated_metadata
    else:
        print(f"{metadata} is not found in confluence")
        sys.exit(1)


def upload_image(markdown_file_path, markdown_text, metadata, pat):
    source_folder = os.path.dirname(os.path.abspath(markdown_file_path))
    for tag in re.findall(r"\!\[.*?\]\(.*?\)", markdown_text):
        rel_path = re.search(r"\((.*?)\)", tag).group(1)
        alt_text = re.search(r"\[(.*?)\]", tag).group(1)
        abs_path = os.path.join(source_folder, rel_path)
        if rel_path.startswith("http") or rel_path.startswith("/"):
            continue
        params = metadata | {"file_path": abs_path, "comment": alt_text, "pat": pat}
        api.upsert_attachment(**params)

    for tag in re.findall(r"<img.*?\/>", markdown_text):
        rel_path = re.search(r'src="(.*?)"', tag).group(1)
        alt_text = re.search(r'alt="(.*?)"', tag).group(1)
        abs_path = os.path.join(source_folder, rel_path)
        if rel_path.startswith("http") or rel_path.startswith("/"):
            continue
        params = metadata | {"file_path": abs_path, "comment": alt_text, "pat": pat}
        api.upsert_attachment(**params)


def save_markdown(file_path, markdown_data):
    with open(file_path, "w") as f:
        f.write(frontmatter.dumps(markdown_data))


def read_markdown(file_path):
    with open(file_path, "r") as f:
        markdown_data = frontmatter.load(f)
        return markdown_data


def read_pat(file_path):
    with open(file_path, "r") as f:
        return f.read()


main(parser.parse_args())
