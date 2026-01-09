import os
import shutil
import re
from block_markdown import (markdown_to_html_node)

def copy_files_recursive(source_dir_path, dest_dir_path):
    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)

    for filename in os.listdir(source_dir_path):
        from_path = os.path.join(source_dir_path, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        print(f" * {from_path} -> {dest_path}")
        if os.path.isfile(from_path):
            shutil.copy(from_path, dest_path)
        else:
            copy_files_recursive(from_path, dest_path)


def extract_title(markdown):
    '''
    Docstring for extract_title
    Goal: It should pull the h1 header from the markdown file 

    :param markdown: markdown file
    '''
    
    # will match:
    # - start of line ^, 
    # - one # character, 
    # - \s+ one or more whitespaces,
    # - .* any char except new line
    # I was having issues with re.match but re.findall worked
    title = re.findall(r"^#{1}\s+.*", markdown, re.MULTILINE)
    if len(title) < 1:
        raise Exception("There is no H1 header")

    return title[0].replace("#", "").strip()

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"generate_page * {from_path} {template_path} -> {dest_path}")
    from_file = open(from_path, "r")
    markdown_content = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    template = template.replace('href="/', 'href="' + basepath)
    template = template.replace('src="/', 'src="' + basepath)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    
    #Crawl every entry in the content directory

    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)

    for filename in os.listdir(dir_path_content):
        new_filename = filename.split(".")[0] + ".html"
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(from_path):
            dest_path_html = os.path.join(dest_dir_path, new_filename)
            generate_page(from_path, template_path, dest_path_html, basepath)
        else:
            generate_pages_recursive(from_path, template_path, dest_path, basepath)