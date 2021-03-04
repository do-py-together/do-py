"""
Build the do-py readme dynamically using the examples specified in the template file.
"""
import os

from do_py import DataObject, R


ROOT = os.path.abspath(__file__).replace('/examples/build_readme.py', '')
DOCSTRING_DELIM = '"""\n'
EXAMPLE_PREFIX = '//example='


class ExampleFile(DataObject):
    _restrictions = {
        'file_name': R.STR,
        'lines': R.LIST
        }

    @classmethod
    def from_file_name(cls, file_name):
        """
        :rtype: ExampleFile
        """
        lines = []
        with open('{root}/examples/{file_name}'.format(root=ROOT, file_name=file_name)) as f:
            lines.extend(f.readlines())
        return cls({
            'file_name': file_name,
            'lines': lines
            })

    @property
    def doc(self):
        """
        :rtype: list of str
        """
        doc_lines = []
        if self.lines[0] == DOCSTRING_DELIM:
            for line in self.lines[1:]:
                if line == DOCSTRING_DELIM:
                    break
                if len(doc_lines) == 0:
                    line = '### %s' % line
                doc_lines.append(line)
        return doc_lines

    @property
    def body(self):
        """
        :rtype: list of str
        """
        doc = 0
        body = []
        for line in self.lines:
            if line == DOCSTRING_DELIM:
                doc += 1
                continue
            if doc == 2:
                body.append(line)
        return body


def main():
    with open('%s/examples/template_readme.md' % ROOT, 'r') as template_file:
        template_readme = template_file.readlines()

    readme = []
    for line in template_readme:
        if line.startswith(EXAMPLE_PREFIX):
            example_file_name = line.replace(EXAMPLE_PREFIX, '').replace('\n', '')
            example_file = ExampleFile.from_file_name(example_file_name)
            readme.extend(example_file.doc)
            readme.append('```python\n')
            readme.extend(example_file.body)
            readme.append('```\n')
            readme.append('\n')
            readme.append('\n')
        else:
            readme.append(line)

    with open('%s/README.md' % ROOT, 'w+') as result_readme_file:
        result_readme_file.writelines(readme)


if __name__ == '__main__':
    main()
