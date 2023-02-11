import os
import re

import markdown


def to_html(markdown_text, id=None):
    html = markdown.markdown(
        markdown_text, extensions=["tables", "fenced_code", "footnotes"]
    )
    html = convert_comment_block(html)
    html = convert_code_block(html)
    html = convert_table_of_content(html)
    html = convert_image_tag(html, id)
    return html


def convert_comment_block(html):
    """
    Convert markdown code bloc to Confluence hidden comment

    :param html: string
    :return: modified html string
    """
    open_tag = "<ac:placeholder>"
    close_tag = "</ac:placeholder>"

    html = html.replace("<!--", open_tag).replace("-->", close_tag)

    return html


def convert_code_block(html):
    """
    Convert html code blocks to Confluence macros

    :param html: string
    :return: modified html string
    """
    code_blocks = re.findall(r"<pre><code.*?>.*?</code></pre>", html, re.DOTALL)
    if code_blocks:
        for tag in code_blocks:
            lang = re.search('code class="language-(.*)"', tag)
            if lang:
                lang = lang.group(1)
            else:
                lang = "none"
            content = re.search(
                r"<pre><code.*?>(.*?)</code></pre>", tag, re.DOTALL
            ).group(1)
            conf_ml = """\
                    <ac:structured-macro ac:name="code">
                        <ac:parameter ac:name="theme">Midnight</ac:parameter>
                        <ac:parameter ac:name="linenumbers">true</ac:parameter>
                        <ac:parameter ac:name="language">{lang}</ac:parameter>
                        <ac:plain-text-body><![CDATA[{content}]]></ac:plain-text-body>
                    </ac:structured-macro>
                """

            conf_ml = "\n".join([m.lstrip() for m in conf_ml.split("\n")]).format(
                lang=lang, content=content
            )
            conf_ml = conf_ml.replace("&lt;", "<").replace("&gt;", ">")
            conf_ml = conf_ml.replace("&quot;", '"').replace("&amp;", "&")
            html = html.replace(tag, conf_ml)

    return html


def convert_table_of_content(html):
    html = re.sub(
        r"<p>\[TOC\]</p>",
        '<p><ac:structured-macro ac:name="toc" ac:schema-version="1"/></p>',
        html,
        1,
    )

    return html


def convert_image_tag(html, id):
    if not id:
        return html
    for tag in re.findall("<img(.*?)\/>", html):
        rel_path = re.search('src="(.*?)"', tag).group(1)
        basename = os.path.basename(rel_path)
        if re.search("http.*", rel_path) is None:
            replaced_tag = tag.replace(
                rel_path, f"/download/attachments/{id}/{basename}"
            )
            html = html.replace(tag, replaced_tag)
    return html
