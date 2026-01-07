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
    '''
    Docstring for markdown_to_blocks
    
    :param markdown: It takes a raw Markdown string (representing a full document)
    :returns: a list of "block" strings
    '''
    #split the markdown to blocks, consider only those non missing, and strip them at the end
    return [block.strip() for block in markdown.split("\n\n") if block != ""]


def block_to_block_type(block):
    '''
    Docstring for block_to_block_type
    
    :param block: single block of markdown text
    :returns: BlockType representing type of block it is
    '''
    match block:
        # Heading: Starts with 1-6 # characters followed by a space
        case _ if re.match(r"^#{1,6} ", block):
            return BlockType.HEADING

        # Multiline Code blocks must start with 3 backticks and a newline, then end with 3 backticks.
        # [\s\S]* matches any character including newlines
        case _ if re.match(r"^```\n[\s\S]*```$", block):
            return BlockType.CODE

        # Every line in a quote block must start with a "greater-than" character and a space: >
        # Pattern checks for "> " followed by content, then a newline or end of string, repeated for all lines.
        case _ if re.match(r"^(> .*(\n|$))+$", block):
            return BlockType.QUOTE

        # Every line in an unordered list block must start with a - character, followed by a space.
        case _ if re.match(r"^(- .*(\n|$))+$", block):
            return BlockType.ULIST

        # Every line in an ordered list block must start with a number followed by a . character and a space. The number must start at 1 and increment by 1 for each line.
        # Note: Validating the specific 'increment by 1' logic (1., 2., 3.) is complex 
        # for pure regex. This pattern ensures the structural format "Number. Content".
        case _ if re.match(r"^(\d+\. .*(\n|$))+$", block):
            # Optional: strict check for 1, 2, 3 incrementation
            lines = block.split('\n')
            is_incremental = True
            for i, line in enumerate(lines):
                if not line.startswith(f"{i+1}. "):
                    is_incremental = False
                    break
            
            if is_incremental:
                return BlockType.OLIST
            else:
                return BlockType.PARAGRAPH

        # 6. Paragraph: Fallback for everything else
        case _:
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
