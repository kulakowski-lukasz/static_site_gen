import re
from textnode import TextType, TextNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    '''
    *** GOAL: 

    *** this: 
    node = TextNode("This is text with a `code block` word", TextType.TEXT)
    new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

    *** becomes this
    [
        TextNode("This is text with a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" word", TextType.TEXT),
    ]
    '''
    new_nodes = []
    for old_node in old_nodes:
        #if its not TEXT, add to results as is, we process TEXT only
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)

        #we expect that the split will give uneven number 
        #Ok, I get this now - it will always be uneven, it can be that last value is just empty string ...
        #... in cases where the enclosed words are last in the old_node.text 
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        
        #iterate over sections and ...
        for i in range(len(sections)):
            #... for those empty sections, do nothing - this can happen
            if sections[i] == "":
                continue
            #... sections that are even, are regular text always
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            #... uneven sections ar always the ones with the given type
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    '''
    GOAL: 
    return the tuple of text and image url from markdown text
    Images in markdown look like: ![Description of image](url/of/image.jpg)
    '''
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    '''
    GOAL: 
    return the href from markdown text
    Links in markdown look like: This is a paragraph with a [link](https://www.google.com).

    *** this:
    "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"

    *** becomes this:
    [
        ("link", "https://boot.dev"),
        ("another link", "https://blog.boot.dev"),
    ],
    '''
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def split_nodes_image(old_nodes):
    '''
    GOAL:
    similar to split_nodes_delimiter, but splits nodes based on the image references

    *** this:
    node = TextNode(
    "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
    TextType.TEXT,
    )
    new_nodes = split_nodes_link([node])

    *** becomes this
    [
        TextNode("This is text with a link ", TextType.TEXT),
        TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
        TextNode(" and ", TextType.TEXT),
        TextNode(
            "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
        ),
    ]
    '''
    new_nodes = []
    for old_node in old_nodes:

        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        images = extract_markdown_images(original_text)

        #if there are no images - its just text so append to the result
        if len(images) == 0:
            new_nodes.append(old_node)
            continue

        
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)

            #there must be 2 items in the list after split, if not raise error
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            
            #if first element is not empty, add it as a text
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            #add the image
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )

            #in the next iteration of the loop, overwrite the original text with the remaining text
            original_text = sections[1]

        #if there is something left, then it was not splitted i.e. no image there - just add as a text
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    '''
    GOAL:
    similar to split_nodes_delimiter, but splits nodes based on the link references
    '''
    new_nodes = []
    for old_node in old_nodes:

        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        links = extract_markdown_links(original_text)

        #if there are no links - its just text so append to the result
        if len(links) == 0:
            new_nodes.append(old_node)
            continue

        
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)

            #there must be 2 items in the list after split, if not raise error
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            
            #if first element is not empty, add it as a text
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            #add the link
            new_nodes.append(TextNode(link[0],TextType.LINK,link[1],))

            #in the next iteration of the loop, overwrite the original text with the remaining text
            original_text = sections[1]

        #if there is something left, then it was not splitted i.e. no image there - just add as a text
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    '''
    GOAL: turn the text into TextNodes
    '''
    # initialize the first text node with the whole text
    nodes = [TextNode(text, TextType.TEXT)]

    ### pefrom all the splits on delimiters 
    # bold 
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    # italic
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    # code
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    ### split on images
    nodes = split_nodes_image(nodes)

    ### split on links
    nodes = split_nodes_link(nodes)

    
    return nodes