import re 
from enum import (Enum)
from inline_markdown import (text_to_textnodes)
from htmlnode import (ParentNode)
from textnode import (TextType, TextNode, text_node_to_html_node)

#enum of text types
class BlockType(Enum):
    PARAGRAPH   = "paragraph"
    HEADING     = "heading"
    CODE        = "code"
    QUOTE       = "quote"
    ULIST       = "unordered_list"
    OLIST       = "ordered_list"



def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    '''
    Docstring for markdown_to_html_node
    Goal: split markdown into blocks, turn them into HTMLNodes

    :param markdown: string representing Markdown
    :returns: One giant parent node with all blocks as chlidren
    '''
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        #call the aggregated function to turn block into HTMLNode, it will call severa support functions for this
        html_node = block_to_html_node(block)
        children.append(html_node)
    #everything will be just under <div> 
    return ParentNode("div", children, None)


def block_to_html_node(block):
    '''
    Docstring for block_to_html_node
    Goal: main function to aggregate all helpers that turn block of different type into HTMLNodes

    :param block: a block from Markdown
    :returns: call to a helper function creating HTMLNode
    '''
    #read the type of the block first
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.OLIST:
        return olist_to_html_node(block)
    if block_type == BlockType.ULIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")




def text_to_children(text):
    '''
    Docstring for text_to_children
    Goal: turn the given text into chlidren first (text nodes) and then into html leaf nodes
    This handles the inline markdown of the givne block, by calling text_to_textnodes from inline_markdown module
    and then text_node_to_html_node from textnode module

    :param text: text string - coming from a given block
    '''
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children



### Helper functions to create the HTML nodes
def paragraph_to_html_node(block):
    '''
    Docstring for paragraph_to_html_node
    Goal: turn paragraph block into a parent node with its chilren
    
    :param block: block from MD
    '''
    #split block into list by new lines
    lines = block.split("\n")
    #join them all together, but space separated
    paragraph = " ".join(lines)

    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    '''
    Docstring for heading_to_html_node
    Turn a heading block into a parent node with its children
    A heading is a parent itself, and as we've built parents - parent has no value
    So a text in the heading is a children itself

    :param block: block from MD
    '''
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    '''
    Docstring for code_to_html_node
    Goal: turn code block into HTML node 
    
    :param block: block from MD
    '''
    #check the code block, a bit redundant but okay
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    
    #retrieve the text
    text = block[4:-3]

    #create a text node and turn into a html child (leaf node)
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    '''
    Docstring for olist_to_html_node
    Goal: turn ordered md list into HTML node

    :param block: block from MD
    '''
    #split by newline char, turn the list items into nodes using text_to_children (inline_markdown)
    items = block.split("\n")
    html_items = []
    for item in items:
        parts = item.split(". ", 1)
        text = parts[1]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    #build ordered list with list itesm as children
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    '''
    Docstring for ulist_to_html_node
    Goal: turn unordered md list into HTML node


    :param block: block from MD
    '''
    #split by newline char, turn the list items into nodes using text_to_children (inline_markdown)
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    '''
    Docstring for quote_to_html_node
    Goal: turn MD citation into HTML node

    :param block: block from MD
    '''
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)
