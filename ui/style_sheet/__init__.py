class StyleSheet(object):
    def __init__(self, styles: dict = None):
        self.styles = styles

    def reformat_style(self, style: dict):
        answer = ""
        name = None
        for key, value in style.items():
            if key == "name":
                name = value
                continue
            answer += f"{key}: {value};\n"
        answer = answer.strip()
        if name is not None:
            answer = f"{name} {{ {answer} }}"
        return answer

    def union(self, s1, s2):
        style1: dict = self.styles.get(s1, {})
        style2: dict = self.styles.get(s2, {})
        union_style = dict(style1)
        union_style.update(style2)
        return self.reformat_style(union_style)

    def __getattr__(self, item):
        style = self.styles.get(item, None)
        if style is None:
            return ""
        return self.reformat_style(style)
