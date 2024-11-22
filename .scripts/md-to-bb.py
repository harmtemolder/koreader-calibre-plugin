import sys
import re
import os


def markdown_to_bbcode(text):
    # Remove all line breaks to preserve full lines in the output
    text = re.sub(r'(?m)^# (.+)', r'[b][SIZE="7"]\1[/SIZE][/b]', text)  # H1
    text = re.sub(r'(?m)^## (.+)', r'[b][SIZE="3"]\1[/SIZE][/b]', text)  # H2
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

    # Compute the absolute path to the version file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(script_dir, '..', 'version.txt')

    # Read the version from the version file
    if not os.path.exists(version_file):
        print(f"Error: Version file '{version_file}' not found.")
        sys.exit(1)

    with open(version_file, 'r') as vf:
        version = vf.read().strip()

    # Format the version as BBCode
    version_bbcode = f'[b][SIZE="5"]v{version}[/SIZE][/b]\n\n'

    # Read and convert the Markdown input
    with open(input_file, 'r') as f:
        markdown_text = f.read()

    bbcode_text = markdown_to_bbcode(markdown_text)

    # Combine version and BBCode content
    full_bbcode_text = version_bbcode + bbcode_text

    # Write the combined BBCode to the output file
    with open(output_file, 'w') as f:
        f.write(full_bbcode_text)

    print(f"Converting {input_file} to {output_file}")
    print(f"Version: {version}")


if __name__ == "__main__":
    main()
