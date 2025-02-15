from pathlib import Path
import re
import json
from urllib.parse import urljoin


def extract_headers_from_notebook(file_path):
    """Extract headers and their levels from Jupyter notebooks."""
    content = Path(file_path).read_text()
    nb = json.loads(content)
    headers = []

    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            for line in cell["source"]:
                if line.startswith("#"):
                    level = len(re.match(r"^#+", line).group())
                    title = line.lstrip("#").strip()

                    # Create proper document-relative link
                    rel_path = str(file_path.relative_to(Path(__file__).parent.parent.parent))
                    link = rel_path.replace(".ipynb", ".html")

                    # Create URL-friendly anchor
                    anchor = title.replace(" ", "-")
                    anchor = re.sub(r"[^\w\s-]", "", anchor)
                    anchor = re.sub(r"\s+", "-", anchor)

                    # Construct the final link without repeating the path
                    link = f"{link}#{anchor}"
                    headers.append((level, title, link))
    return headers


def extract_headers_from_rst(file_path):
    """Extract headers and their levels from RST files."""
    content = Path(file_path).read_text()
    lines = content.split("\n")
    headers = []

    for i, line in enumerate(lines):
        if i > 0 and set(lines[i - 1]) in {"=", "-", "~", "^"}:
            level = 1 if "=" in lines[i - 1] else 2
            title = line.strip()
            # Create proper document-relative link
            rel_path = str(file_path.relative_to(Path(__file__).parent.parent.parent))
            link = rel_path.replace(".rst", ".html")

            # Create URL-friendly anchor
            anchor = title.replace(" ", "-")
            anchor = re.sub(r"[^\w\s-]", "", anchor)
            anchor = re.sub(r"\s+", "-", anchor)

            # Construct the final link without repeating the path
            link = f"{link}#{anchor}"
            headers.append((level, title, link))
    return headers


def generate_nav_template():
    """Generate navigation template with proper Sphinx links."""
    docs_path = Path(__file__).parent.parent.parent
    current_file_path = Path(__file__).resolve().parent  # Get the current file's directory

    # Extract headers from getting_started.ipynb
    headers = extract_headers_from_notebook(docs_path / "examples/getting_started.ipynb")

    # Add headers from adjusting_parameters.ipynb
    headers.extend(
        extract_headers_from_notebook(docs_path / "examples/adjusting_parameters.ipynb")
    )

    # Function to create a relative link
    def create_relative_link(target_file):
        target_path = Path(target_file)
        try:
            relative_link = str(target_path.relative_to(current_file_path.parent)).replace("\\", "/")
        except ValueError:
            relative_link = str(target_path).replace("\\", "/")
        return relative_link

    # Update headers with correct links
    updated_headers = []
    for level, title, link in headers:
        # Create a relative link for each header
        relative_link = create_relative_link(link)
        updated_headers.append((level, title, relative_link))

    template = """
    <div class="sidebar-tree">
      <p class="caption" role="heading">
        <span class="caption-text">DeepVerse6G</span>
      </p>
      <ul>
        {% for level, title, link in headers %}
        <li class="toctree-l{{ level }}">
          <a class="reference internal" href="{{ link }}">{{ title }}</a>
          {% if loop.index < headers|length and headers[loop.index][0] > level %}
            <ul>
          {% endif %}
          {% if loop.index > 0 and headers[loop.index - 1][0] < level %}
            <li class="toctree-l{{ level }}">
              <a class="reference internal" href="{{ link }}">{{ title }}</a>
            </li>
          {% endif %}
          {% if loop.index < headers|length and headers[loop.index][0] < level %}
            </ul>
          {% endif %}
        </li>
        {% endfor %}
      </ul>
      
      {# Add padding div at the bottom #}
      <div style="padding-bottom: 200px;"></div>
    </div>
    <script>
      document.querySelectorAll('.reference.internal').forEach(function(link) {
          link.addEventListener('click', function(event) {
              event.preventDefault();
              const href = this.getAttribute('href');
              
              // Get the current path and extract the base directory
              const currentPath = window.location.pathname || window.location.href;
              const htmlIndex = currentPath.indexOf('/html/');
              
              if (htmlIndex === -1) {
                  // Fallback if /html/ not found
                  window.location.href = href;
                  return;
              }
              
              // Extract the base path up to /html/
              const basePath = currentPath.substring(0, htmlIndex + 6); // Include /html/
              
              // Clean up the href
              const cleanHref = href.replace(/\.\.\//g, '').replace(/^\/+/, '');
              
              // Construct the final URL
              const newPath = basePath + cleanHref;
              window.location.href = newPath;
          });
      });
    </script>
    """

    nav_path = docs_path / "_templates/sidebar/navigation.html"
    nav_path.parent.mkdir(parents=True, exist_ok=True)

    from jinja2 import Template

    template = Template(template)
    nav_content = template.render(headers=updated_headers)
    nav_path.write_text(nav_content)


if __name__ == "__main__":
    generate_nav_template()
