import random
import sys
import re


class TextNode:

    def __init__(self) -> None:
        self.content = []

    def __str__(self):
        return ''.join(map(str, self.content)) + '\n'

    def get_pure_text(self):
        return ''.join(list(filter(lambda x: type(x) == str, self.content)))

    def print_tab(self, tab: int):
        print('\t' * tab, self.get_pure_text())
        for object in self.content:
            if type(object) == TextNode:
                object.print_tab(tab + 1)

    def make_decision(self):
        highsigns = []
        for i in range(len(self.content)):
            if type(self.content[i]) == TextNode:
                if i >= 2:
                    if self.content[i - 1] == '!' and self.content[i - 2] == '!':
                        highsigns.append(i - 1)
                        highsigns.append(i - 2)
                        answer_string: list = list(self.content[i].make_decision())
                        try: answer_string[0] = answer_string[0].upper()
                        except Exception: pass
                        self.content[i] = ''.join(answer_string)
                    else:
                        self.content[i] = self.content[i].make_decision()
                else:
                    self.content[i] = self.content[i].make_decision()
        for highsign in highsigns:
            self.content.pop(highsign)
        text = ''.join(self.content)
        if self.content[0] == '{':
            words = text[1:-1].split('|')
            # print("words:", words)
            return random.choice(words)
        elif self.content[0] == '[':
            basis = text[1:-1].split('+')
            separator = basis[1]
            content = basis[2].lstrip(' ').split('|')
            random.shuffle(content)
            # print("content:", content)
            #print(separator.join(content))
            return separator.join(content)


class FormatException(Exception):
    pass


def handle_text(text: str) -> None:
    starting_nodes = []
    node_stack = []
    for letter in text:
        if letter == "{" or letter == "[":
            if not node_stack:
                current_node = TextNode()
                current_node.content.append(letter)
                starting_nodes.append(current_node)
                node_stack.append(current_node)
            else:
                current_node = node_stack[-1]
                current_node.content.append(TextNode())
                current_node = current_node.content[-1]
                node_stack.append(current_node)
                current_node.content.append(letter)
        elif letter == "}" or letter == "]":
            if not node_stack:
                raise FormatException
            else:
                current_node = node_stack[-1]
                current_node.content.append(letter)
                node_stack.pop()
        else:
            if node_stack:
                current_node = node_stack[-1]
                current_node.content.append(letter)
            else:
                starting_nodes.append(letter)

    text = ""
    for i in range(len(starting_nodes)):
        node = starting_nodes[i]
        if type(node) == str:
            text += node
        elif type(node) == TextNode:
            if i < 2:
                text += node.make_decision();
            elif starting_nodes[i - 1] == '!' and starting_nodes[i - 2] == '!':
                text = text[:-2]
                answer_string = list(node.make_decision())
                try:
                    answer_string[0] = answer_string[0].upper()
                except Exception: pass;
                text += ''.join(answer_string)
            else:
                text += node.make_decision()
    # print(text)

    i = 1
    while i < len(text) - 1:
        letter = text[i]
        if letter in ['.', ',', ':', ';', '?', '!']:
            if text[i - 1] == ' ':
                text = text[:i - 1] + text[i:]
                i = i - 1
                continue
            if text[i + 1] != ' ':
                text = text[:i + 1] + " " + text[i + 1:]
                i += 1
        if letter == '—':
            if text[i - 1] != ' ':
                text = text[i - 1:] + " " + text[:i - 1]
                i += 1
                continue
            if text[i + 1] != " " or text[i + 1] != ',':
                text = text[:i + 1] + " " + text[i + 1:]
                i += 1
        i += 1
        # print(text, i)
    text = re.sub(" +", " ", text)

    return text


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:])
    try:
        print(handle_text(text))
    except FormatException:
        print('Text is formatted incorrectly')
