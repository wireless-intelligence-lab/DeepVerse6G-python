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
    current_file_path = Path(__file__).resolve().parent

    # Create a structured navigation dictionary
    nav_structure = [
        {
            "title": "Documentation",
            "level": 1,
            "items": [
                {
                    "source": "examples/getting_started.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/adjusting_parameters.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/camera.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/lidar.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/mobility.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/communication.ipynb",
                    "headers": []
                },
                {
                    "source": "examples/radar.ipynb",
                    "headers": []
                },
            ]
        }
    ]

    # Populate headers for each section
    for section in nav_structure[0]["items"]:
        section["headers"] = extract_headers_from_notebook(docs_path / section["source"])

    template = """
    <div class="sidebar-tree">
      <p class="caption" role="heading">
        <span class="caption-text">DeepVerse6G</span>
      </p>
      <ul>
        {% for item in items %}
          {% for level, title, link in item.headers %}
            <li class="toctree-l{{ level }}" style="margin-left: {{ (level - 1) * 12 }}px;">
              <a class="reference internal" href="{{ link }}">{{ title }}</a>
            </li>
          {% endfor %}
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
    nav_content = template.render(items=nav_structure[0]["items"])
    nav_path.write_text(nav_content)


if __name__ == "__main__":
    generate_nav_template()
