import os
import re
import yaml


class MdFile:
    def __init__(self, path):

        if not os.path.exists(os.path.abspath(path)):
            print("Md file", os.path.abspath(path), "does not exist!")
            return


        self.rel_path = path
        self.abs_path = os.path.abspath(path)
        self.dir = os.path.dirname(path)
        self.abs_dir = os.path.dirname(self.abs_path)
        self.basename = os.path.basename(path)
        self.content = open(path).read()
        self.basename_no_ext = os.path.splitext(self.basename)[0]

#         print("mdfile path:", path)
#         print("mdfile dir:", self.dir)


        self.title = ''
        self.cover_path = ''
        self.bibliography = ''

        self.read_front_matter()


    def read_front_matter(self):
        match = re.match('^---\n([\s\S]*?)\n---', self.content)
        if match:
            #delete fron matter
#             self.content = re.sub('^---\n([\s\S]*?)\n---', '', self.content)
            front_matter = yaml.safe_load(match.groups()[0])
            if 'title' in front_matter:
                self.title = front_matter['title']
            if 'cover' in front_matter:
                self.cover_path = front_matter['cover']
            if 'bibliography' in front_matter:
                self.bibliography = front_matter['bibliography']


    def exec_embeded_scripts(self):
        output = ""
        in_script = False

        for line in self.content.split('\n'):
            if line.strip() == "%%% START":
                in_script = True
                continue

            if line.strip() == "%%% STOP":
                in_script = False
                continue

            if in_script:
                output = output + os.popen(line).read()
            else:
                output = output + line + '\n'

        self.content = output


    def insert_files(self):
        output = ""
        for line in self.content.split('\n'):
            match = re.match(r'^%%% INSERT (.+)', line)
            if match:
                if match.groups()[0][0] != '/':  # relative path
                    insert_fn = os.path.join(self.abs_dir,  match.groups()[0])
                else:
                    insert_fn = match.groups()[0]

                print("inserting", insert_fn)
                insert_file_content = open(insert_fn, 'r').read()
                output = output + insert_file_content
            else:
                output = output + line + '\n'
        self.content = output


    def remove_percent_comments(self):
        output = ""
        for line in self.content.split('\n'):
            if not line:
                output += '\n'
                continue
            if not (line[0] == '%' and line[1] == '%'):
                output = output + line + '\n'


        self.content = output

