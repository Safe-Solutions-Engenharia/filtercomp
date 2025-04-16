# Update Documentation

## Understanging Project Structure

```bash
documentation-default/
├── docs/
│   ├── index.md
│   └── assets/
│       └── images/
├── mkdocs.yml
├── requirements.txt
└── README.md
```

The `docs/` folder contains all Markdown source files from each page of the documentation. The `mkdocs.yml` file contains the configuration for the documentation name, theme, navigation and plugings.

---

## Editing Documentation

All documentation is written in Markdown (`.md`). For example, `index.md` might look like:

```md title="index.md"
# Welcome

This is the homepage of your MkDocs documentation.
```

Always use Markdown syntax to add headings, links, images, tables, and more.

---

## Adding Pages and Navigation

In `mkdocs.yml`, define the order of the documentation structure:

```yaml title="mkdocs.yml" linenums="8"
nav:
  - Home: index.md
  - Setup Guide: setup.md
  - Editing Guide: update-documentation.md
  - Deploy Example: deployment.md
```

---

## Further Reading

To learn more about specific plugins and Markdown syntax, check out the the [mkdocs documentation](https://www.mkdocs.org/).