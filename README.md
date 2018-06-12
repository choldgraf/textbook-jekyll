# The Data 8 Jekyll textbook

This repository holds a Jekyll-based version of the Data 8 textbook.

All textbook content is primarily stored in Jupyter notebooks in the `notebooks/` folder.
This can be converted to Jekyll-ready markdown by running the following command:

```
python scripts/generate_textbook.py
```

This will:

* Run `nbconvert` to turn the `.ipynb` files into markdown
* Replace relative image file paths with a `{{ site.baseurl }}` base for Jekyll
* Clean up formatting issues for displaying properly
* Generate the yaml for the site sidebar automatically

You can the push the changes to GitHub, which will automatically build a Jekyll site with
your newly-created Markdown files. Alternatively, you can preview your built site
using Jekyll on your computer by taking the following steps:

1. Ensure that Jekyll and Ruby are installed. [See the Jekyll docs](https://jekyllrb.com/docs/installation/) for information on this.
2. Ensure that your notebooks have been converted to markdown:

   ```
   python scripts/generate_textbook.py
   ```
3. Run the Jekyll site preview command:

   ```
   bundle exec jekyll serve
   ```

This should open up a port on your computer with a live version of the textbook.

## Relevant files

* `_config.yml` contains all site configuration.
* `_data/navigation.yml` contains site navigation as well as auto-generated sidebar yaml
* `notebooks/` contain all course content in Jupyter notebook form
* `textbook/` contain notebooks converted to markdown
* `scripts/` contains scripts to generate the textbook from the Jupyter notebooks
