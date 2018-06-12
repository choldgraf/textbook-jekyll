from subprocess import check_call
import os
import os.path as op
import shutil as sh
import yaml
from glob import glob
import nbformat as nbf
from nbclean import NotebookCleaner
from tqdm import tqdm
import numpy as np
import argparse
DESCRIPTION = ("Convert a collection of Jupyter Notebooks into Jekyll "
               "markdown suitable for a course textbook.")

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument("site_root", help="Path to the root of the course repository.")
parser.add_argument("--overwrite", action='store_true', help="Overwrite md files if they already exist.")
parser.add_argument("--execute", action='store_true', help="Execute notebooks before converting to MD.")
parser.set_defaults(overwrite=False, execute=False)


def _markdown_to_files(path_markdown, indent=2):
    """Takes a markdown file containing chapters/sub-headings and
    converts it to a file structure we can use to build a side bar."""

    with open(path_markdown, 'r') as ff:
        lines = ff.readlines()

    files = []
    for line in lines:
        if line.strip().startswith('* '):
            title = _between_symbols(line, '[', ']')
            link = _between_symbols(line, '(', ')')
            spaces = len(line) - len(line.lstrip(' '))
            level = spaces / indent
            files.append((title, link, level))
    return files


def _strip_suffixes(string, suffixes=None):
    suffixes = ['.ipynb', '.md'] if suffixes is None else suffixes
    for suff in suffixes:
        string = string.replace(suff, '')
    return string

def _clean_lines(lines):
    """Replace images with jekyll image root and add escape chars as needed."""
    IMG_STRINGS = [ii*'../' + IMAGES_FOLDER for ii in range(4)]
    inline_replace_chars = ['#']
    for ii, line in enumerate(lines):
        # Images: replace relative image paths to baseurl paths
        for IMG_STRING in IMG_STRINGS:
            line = line.replace(IMG_STRING, '{{ site.baseurl }}/images')

        dollars = np.where(['$' == char for char in line])[0]
        # Make sure we have at least two dollar signs and they
        # Aren't right next to each other
        if len(dollars) > 2 and all(ii > 1 for ii in (dollars[1:] - dollars[:1])):
            for char in inline_replace_chars:
                line = line.replace('\\#', '\\\\#')
        lines[ii] = line
    return lines


def _generate_sidebar(files):
    sidebar_text = ['sidebar-textbook:']
    sp = '  '
    chapter_ix = 1
    for ix_file, (title, link, level) in tqdm(list(enumerate(files))):
        # Force double quotes
        title = title.replace("'", '"')
        if level > 0 and len(link) == 0:
            continue
        if level == 0:
            if site_yaml.get('number_chapters', False) is True:
                title = '{}. {}'.format(chapter_ix, title)
            chapter_ix += 1
        new_link = link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME)
        new_link = _strip_suffixes(new_link).strip('.')
        print(link, '\n', new_link)
        space = '  ' if level == 0 else '    '
        level = int(level)
        sidebar_text.append(space + "- title: '{}'".format(title))
        sidebar_text.append(space + '  class: level_{}'.format(level))
        if len(link) > 0:
            sidebar_text.append(space + '  url: {}'.format(new_link))
        if ix_file != (len(files) - 1) and level == 0 and level < files[ix_file + 1][-1]:
            sidebar_text.append(space + '  children:')
    sidebar_text = [ii + '\n' for ii in sidebar_text]
    return sidebar_text


def _between_symbols(string, c1, c2):
    """Will return empty string if nothing is between c1 and c2."""
    for char in [c1, c2]:
        if char not in string:
            raise ValueError("Couldn't find character {} in string {}".format(
                char, string))
    return string[string.index(c1)+1:string.index(c2)]


def _clean_notebook(notebook):
    cleaner = NotebookCleaner(notebook)
    cleaner.remove_cells(empty=True)
    cleaner.remove_cells(search_text="# HIDDEN")
    cleaner.clear('stderr')
    cleaner.save(notebook)
    return notebook


if __name__ == '__main__':
    args = parser.parse_args()
    overwrite = bool(args.overwrite)
    execute = bool(args.execute)

    # Paths for our notebooks
    SITE_ROOT = op.abspath(args.site_root)
    SITE_NAVIGATION = op.join(SITE_ROOT, '_data', 'navigation.yml')
    CONFIG_FILE = op.join(SITE_ROOT, '_config.yml')
    TEMPLATE_PATH = op.join(SITE_ROOT, 'assets', 'templates', 'jekyllmd.tpl')
    TEXTBOOK_FOLDER_NAME = 'textbook'
    NOTEBOOKS_FOLDER_NAME = 'notebooks'
    TEXTBOOK_FOLDER = op.join(SITE_ROOT, TEXTBOOK_FOLDER_NAME)
    NOTEBOOKS_FOLDER = op.join(SITE_ROOT, NOTEBOOKS_FOLDER_NAME)
    IMAGES_FOLDER = op.join(SITE_ROOT, 'images')
    MARKDOWN_FILE = op.join(SITE_ROOT, 'SUMMARY.md')

    # Load the yaml for this site
    with open(CONFIG_FILE, 'r') as ff:
        site_yaml = yaml.load(ff.read())

    # --- Collect the files we'll convert over ---
    files = _markdown_to_files(MARKDOWN_FILE)

    # --- Loop through all ipynb/md files, convert to md as necessary and copy. ---
    for ix_file, (title, link, level) in tqdm(list(enumerate(files))):
        if len(link) == 0:
            continue
        if not op.exists(link):
            raise ValueError("Could not find file {}".format(link))

        # Check new folder / file path
        filename = op.basename(link)
        new_folder = op.dirname(link).replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME)
        new_file_path = op.join(new_folder, filename.replace('.ipynb', '.md'))
        if overwrite is True and op.exists(new_file_path):
            continue

        if not op.isdir(new_folder):
            os.makedirs(new_folder)

        # Collect previous/next md file for pagination
        if ix_file == 0:
            prev_file_link = ''
            prev_file_title = ''
        else:
            prev_file_title, prev_file_link, _ = files[ix_file-1]
            prev_file_link = _strip_suffixes(prev_file_link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME))

        if ix_file == len(files) - 1:
            next_file_link = ''
            next_file_title = ''
        else:
            next_file_title, next_file_link, _ = files[ix_file+1]
            next_file_link = _strip_suffixes(next_file_link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME))

        # Convert notebooks or just copy md if no notebook.
        if link.endswith('.ipynb'):
            # Create a temporary version of the notebook we can modify
            tmp_notebook = link + '_TMP'
            sh.copy2(link, tmp_notebook)

            # Clean up the file before converting
            _clean_notebook(tmp_notebook)

            # Run nbconvert moving it to the output folder
            build_call = '--FilesWriter.build_directory={}'.format(new_folder)
            images_call = '--NbConvertApp.output_files_dir={}'.format(
                op.join(IMAGES_FOLDER, new_folder))
            call = ['jupyter', 'nbconvert', '--log-level="CRITICAL"',
                    '--to', 'markdown', '--template', TEMPLATE_PATH,
                    images_call, build_call, tmp_notebook]
            if execute is True:
                call.insert(-1, '--execute')
            check_call(call)
            os.remove(tmp_notebook)
        elif link.endswith('.md'):
            # If a non-notebook file, just copy it over.
            # If markdown we'll add frontmatter later
            sh.copy2(link, new_file_path)
        else:
            raise ValueError("Files must end in ipynb or md")

        # Extra slash to the inline math before `#` since Jekyll strips it
        with open(new_file_path, 'r') as ff:
            lines = ff.readlines()
        lines = _clean_lines(lines)

        # Front-matter YAML
        yaml = []
        yaml += ['---']
        yaml += ['layout: textbook']
        if link.endswith('.ipynb'):
            yaml += ['interact_link: {}'.format(link.lstrip('./'))]
        yaml += ['previous:']
        yaml += ['  url: {}'.format(prev_file_link.lstrip('.').replace('"', "'"))]
        yaml += ["  title: '{}'".format(prev_file_title)]
        yaml += ['next:']
        yaml += ['  url: {}'.format(next_file_link.lstrip('.').replace('"', "'"))]
        yaml += ["  title: '{}'".format(next_file_title)]
        yaml += ['sidebar:']
        yaml += ['  nav: sidebar-textbook']
        yaml += ['---']
        yaml = [ii + '\n' for ii in yaml]
        lines = yaml + lines

        # Write the result
        with open(new_file_path, 'w') as ff:
            ff.writelines(lines)

    # Generate sidebar, replacing the old one if it exists
    sidebar_text = _generate_sidebar(files)

    with open(SITE_NAVIGATION, 'r') as ff:
        lines = ff.readlines()

    text_start = np.where(['# --- Textbook sidebar ---' in line for line in lines])[0][0]
    lines = lines[:text_start+1] + sidebar_text

    with open(SITE_NAVIGATION, 'w') as ff:
        ff.writelines(lines)
    print('Done generating sidebar...')
    print('Done!')
