import sys
import re


def markdown_to_bbcode(text):
    # Remove all line breaks to preserve full lines in the output
    text = re.sub(r'(?m)^# (.+)', r'[b][SIZE="7"]\1[/SIZE][/b]', text)  # H1
    text = re.sub(r'(?m)^## (.+)', r'[b][SIZE="5"]\1[/SIZE][/b]', text)  # H2
    text = re.sub(r'(?m)^### (.+)', r'[b][SIZE="3"]\1[/SIZE][/b]', text)  # H3

    # Convert Markdown lists to BBCode
    text = re.sub(r'(?m)^\* (.+)', r'[list][*]\1[/list]', text)  # Unordered list
    text = re.sub(r'(?m)^\d+\. (.+)', r'[list][*]\1[/list]', text)  # Ordered list

    # Convert Markdown links to BBCode
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[url=\2]\1[/url]', text)

    # Convert Markdown bold and italic to BBCode
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'\*(.+?)\*', r'[i]\1[/i]', text)

    return text


def main():
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_bbcode.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        markdown_text = f.read()

    bbcode_text = markdown_to_bbcode(markdown_text)

    # Write the BBCode to the output file
    with open(output_file, 'w') as f:
        f.write(bbcode_text)


if __name__ == "__main__":
    main()
