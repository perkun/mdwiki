import re
import os
import shutil
import json
from libmdwiki.utils import hash_filename

# TODO remove that

# def get_wikis():
#     wikis_raw = ''
#     with open("/home/perkun/.config/nvim/vimwiki.vim") as f:
#         wikis_raw = f.read()
#     wikis_raw = wikis_raw.replace('let g:vimwiki_list = ', '').replace(
#         '\n', '').replace('\\', '').replace('\'', '"')
#     return json.loads(wikis_raw)
# WIKIS = get_wikis()


URL_REGEX = re.compile(
    r'^((?:http|ftp)s?://|www\.)'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Link:
    def __init__(self, raw_link=None, description=None, destination=None,
                 link_type=None):

        self.valid = False

        self.type_web = False
        self.type_img = False
        self.type_absolute = False
        self.type_file = False
        self.type_md = False
        self.type_wiki = False

        if description != None and destination != None:
            self.description = description
            self.destination = destination
        else:
            self.description = ''
            self.destination = ''

        if link_type != None:
            if link_type == 'img':
                self.type_img = True

        if raw_link:
            self.raw_link = raw_link.strip()
            self.parse_md(self.raw_link)


    def parse_md(self, raw_link):
        match = re.match(r".?\[(.+)\]\((.+)\)", raw_link)
        if match:
            self.valid = True

            if raw_link[0] == '!':
                self.type_img = True

            self.description = match.groups()[0]
            self.destination = match.groups()[1]

            if re.match(URL_REGEX, self.destination):
                self.type_web = True

            if re.match(r'.+\.md', self.destination):
                self.type_md = True

            if re.match(r'^/', self.destination):
                self.type_absolute = True

            if re.match(r'^file:', self.destination):
                self.type_file = True
                # remove "file" from link
                self.destination = self.destination.replace('file:', '', 1)

            if re.match(r'^wiki([0-9])+:', self.destination):
                self.type_wiki = True

#             print(self.description, self.destination)


    def get_link(self, fmt='md', destination=None, prefix=True):
        link_prefix = ''
        dest_prefix = ''

        if destination == None:
            dest = self.destination
        else:
            dest = destination

        if self.type_file and prefix:
            dest_prefix = 'file:'

        if fmt == 'md':
            if self.type_img:
                link_prefix = '!'
            return link_prefix + f'[{self.description}]({dest_prefix}{dest})'
        elif fmt == 'html':
            return f'<a href="{dest}"> {self.description} </a>'


    def destination_to_html(self, text):
        new_dest = os.path.splitext(self.destination)[0] + ".html"
        return text.replace(self.get_link(), self.get_link(destination=new_dest,
                            prefix=False))


    def update_destination(self, text, new_dest):
        if self.type_img:
            line =  text.replace(self.get_link(),
                                 self.get_link(destination=new_dest,
                                               prefix=False))
            self.destination = new_dest
            return line
        else:
            line =  text.replace(self.get_link(),
                                 self.get_link(destination=new_dest,
                                               prefix=False))
            self.destination = new_dest
            return line


    def copy_resources(self, line, resources_dir, base_url, directory):
        if not self.type_img and not self.type_file:
            return line

        source = os.path.join(directory, self.destination)
        new_basename = hash_filename(source)
        dest_local = os.path.join(resources_dir, new_basename)
        shutil.copyfile(source, dest_local)

        dest = os.path.join(base_url, "resources", new_basename)
        line =  self.update_destination(line, dest)
        return line


    def make_wiki_links(self, base_url, line):
        match = re.match("^wiki([0-9])+:(.+)", self.destination)
        if match:
            wiki_nr = int(match.groups()[0])
            ext_wiki_page = match.groups()[1]

            print(f"external wiki: {wiki_nr}; page: {ext_wiki_page}")
            if wiki_nr >= len(WIKIS):
                print("external wiki ID={wiki_nr} is to big")
                exit()

           # TODO
           # this is a hack... the output dir of another wiki
            ext_wiki_url = os.path.join(base_url, "../")
            print(ext_wiki_url)
            ext_wiki_url = os.path.join(ext_wiki_url, f'wiki{wiki_nr}',
                    os.path.splitext(ext_wiki_page)[0] + ".html")
            return self.update_destination(line, ext_wiki_url)

        return line

