# OpenTiny - Open Source Static Tiny URL Shorter
# Usage: python generate.py -j url.json -o _site -t template.html --error-page 404.html
import os
import json
import shutil
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate site structure from a JSON file.")
    parser.add_argument('-j', '--json-file', type=str, default='url.json', 
                        help="Path to the JSON file (default: url.json)")
    parser.add_argument('-o', '--parent-folder', type=str, default='_site', 
                        help="Parent folder name (default: _site)")
    parser.add_argument('-t', '--template-file', type=str, default='template.html', 
                        help="Template file path (default: template.html)")
    parser.add_argument('--error-page', type=str, default='404.html', 
                        help="Error page file path (default: 404.html)")
    parser.add_argument('-p', '--print', action='store_true', 
                        help="Print details of the generated files")
    return parser.parse_args()

# Main function
def main():
    # Parse command-line arguments
    args = parse_arguments()
    json_file = args.json_file
    parent_folder = args.parent_folder
    template_file = args.template_file
    error_page_file = args.error_page

    # Remove the parent folder if it exists, then recreate it
    if os.path.exists(parent_folder):
        shutil.rmtree(parent_folder)
        print(f"Folder '{parent_folder}' removed.")
        
    os.makedirs(parent_folder)
    print(f"Folder '{parent_folder}' created.")

    # Copy the 404.html file into the _site folder
    if os.path.exists(error_page_file):
        shutil.copy(error_page_file, parent_folder)
        print(f"File '{error_page_file}' copied to '{parent_folder}'.")
    else:
        print(f"Warning: The file '{error_page_file}' does not exist. It was not copied.")

    # Read the JSON file
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            print(f"Contents of {json_file}:")
            print(json.dumps(data, indent=4))
            
            # Read the template file
            with open(template_file, 'r') as template:
                template_content = template.read()

            # Create a folder and an index.html file for each key in the JSON data
            for key, value in data.items():
                if 'url' not in value:
                    print(f"Error: The URL is required for '{key}'. Skipping this entry.")
                    continue  # Skip this entry if URL is not provided

                # Extract optional fields with defaults
                url = value['url']
                title = value.get('title', key)
                description = value.get('description', key)
                image = value.get('image', '')

                folder_path = os.path.join(parent_folder, key)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Folder '{folder_path}' created.")
                else:
                    print(f"Folder '{folder_path}' already exists.")

                # Create index.html in the folder from the template
                index_file_path = os.path.join(folder_path, 'index.html')

                # Replace placeholders in the template
                index_content = template_content.replace('{{ title }}', title) \
                                                .replace('{{ heading }}', title) \
                                                .replace('{{ url }}', url) \
                                                .replace('{{ description }}', description) \
                                                .replace('{{ image }}', image)
                # Write to index.html, overwriting if it exists
                with open(index_file_path, 'w') as index_file:
                    index_file.write(index_content)
                print(f"File '{index_file_path}' created")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' is not a valid JSON file.")

if __name__ == "__main__":
    main()
