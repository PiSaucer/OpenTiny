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
    parser.add_argument('-c', '--config-file', type=str, default='config.json',
                        help="Config file path (default: config.json)")
    parser.add_argument('--error-page', type=str, default='404.html', 
                        help="Error page file path (default: 404.html)")
    parser.add_argument('-s', '--sitemap', type=str, default='sitemap.xml',
                        help="Sitemap file path (default: sitemap.xml)")
    parser.add_argument('-p', '--print', type=bool, default=True,
                        help="Print details of the generated files (default: True)")
    return parser.parse_args()

# Function to load the base URL from config file
def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print(f"Warning: The configuration file '{config_file}' does not exist. Using empty base URL.")
        return ''
    except json.JSONDecodeError:
        print(f"Error: The file '{config_file}' is not a valid JSON file.")
        return ''

# Function to generate a sitemap
def generate_sitemap(data, parent_folder, base_url):
    sitemap_path = os.path.join(parent_folder, 'sitemap.xml')
    pages = []

    for key in data.keys():
        pages.append(key)

    # Create the XML content for the sitemap
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml_content += f'  <url>\n\t\t<loc>{base_url}/{page}/</loc>\n\t</url>\n'
    xml_content += '</urlset>'

    # Write the sitemap to the file
    with open(sitemap_path, 'w') as sitemap_file:
        sitemap_file.write(xml_content)
    return sitemap_path

# Main function
def main():
    # Parse command-line arguments
    args = parse_arguments()
    json_file = args.json_file
    parent_folder = args.parent_folder
    template_file = args.template_file
    error_page_file = args.error_page
    print_details = args.print
    sitemap_path = args.sitemap

    # Load base URL from config file
    config = load_config(args.config_file)
    base_url = config.get('base_url', '')

    # Remove the parent folder if it exists, then recreate it
    if os.path.exists(parent_folder):
        shutil.rmtree(parent_folder)
        if print_details: 
            print(f"Folder '{parent_folder}' removed.")
        
    os.makedirs(parent_folder)
    if print_details: 
        print(f"Folder '{parent_folder}' created.")

    # Copy the 404.html file into the _site folder
    if os.path.exists(error_page_file):
        shutil.copy(error_page_file, parent_folder)
        if print_details: 
            print(f"File '{error_page_file}' copied to '{parent_folder}'.")
    else:
        print(f"Warning: The file '{error_page_file}' does not exist. It was not copied.")

    # Read the JSON file
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            if print_details: 
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

                # Special case for the index key
                if key == "index":
                    index_file_path = os.path.join(parent_folder, 'index.html')
                else:
                    # Create a folder for the key
                    folder_path = os.path.join(parent_folder, key)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        if print_details: print(f"Folder '{folder_path}' created.")
                    else:
                        if print_details: print(f"Folder '{folder_path}' already exists.")
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
                if print_details: print(f"File '{index_file_path}' created")

            # Generate the sitemap after creating all the pages
            sitemap_path = generate_sitemap(data, parent_folder, base_url)
            if print_details: print(f"Sitemap generated at '{sitemap_path}'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' is not a valid JSON file.")

if __name__ == "__main__":
    main()
