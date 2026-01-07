class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if self.props == None or self.props == {}:
            return ""
        return ' ' + ' '.join([f'{k}="{v}"' for k, v in self.props.items()])
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value == "":
            raise ValueError("All leaf nodes must have a value.")
        if self.tag is not None:
            return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
        return f'{self.value}' 

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag == "":
            raise ValueError("All parent nodes must have a tag.")
        else:
            #set current output to empty
            children_output = ""
        
            # Iterate over children (Recursion happens here)
            for child in self.children:
                children_output += child.to_html()
            

            return f"<{self.tag}>{children_output}</{self.tag}>"
