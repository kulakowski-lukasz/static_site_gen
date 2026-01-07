from textnode import TextNode, TextType

def main():
    node = TextNode("This is some anchor text", TextType.TEXT)
    print(node.text_node_to_html_node().to_html())

if __name__ == "__main__":
    main()