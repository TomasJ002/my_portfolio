class HTMLNode:
    def __init__(self, tag: str | None = None, value: str | None = None, children: list["HTMLNode"] | None = None, props: dict[str, str] | None = None,) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if self.props is None:
            return ""
        html = ""
        for key, value in self.props.items():
            html += f' {key}="{value}"'
        return html
    
    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props: dict[str, str] | None = None) -> None:
        super().__init__(tag, value, props = props)
    
    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("Mandatory value attribute is missing or None")
        if self.tag is None:
            return self.value
        if self.tag.lower() == "img":
            return f"<{self.tag}{self.props_to_html()}>"
        else:
            return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
    def __repr__(self) -> str:
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props: dict[str, str] | None = None) -> None:
        super().__init__(tag, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Mandatory tag attribute is missing")
        if not self.children:
            raise ValueError("Mandatory children attribute is missing")
        html = f'<{self.tag}{self.props_to_html()}>'
        for child in self.children:
            html += child.to_html()
        html += f"</{self.tag}>"
        return html
    
    
