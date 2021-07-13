import re
import os
from libmdwiki.utils import mkdir, hash_filename, change_file_ext
from libmdwiki.Link import Link
from libmdwiki.MdFile import MdFile
import pypandoc
import markdown


class Site:
    PROCESSED_FILES = []    # static variable
    PROCESSED_FILE_NAMES = []
    PATH_HASH = {}
    INDEX_PAGE = ''

    def __init__(self, base_url, output_dir, name):
        self.base_url = base_url
        self.output_dir = output_dir
        self.resources_dir = os.path.join(output_dir, "resources")
        self.out_md_file = ""
        self.out_html_file = ""
        mkdir(self.resources_dir)
        self.children = []
        self.name = name
        self.bread_crums = ''
        self.out_filename_md = ''
        self.out_filename_html = ''

        self.mdfile = 0

    def faicons(self, line):
        # fontawesome icons
        return re.sub(r'\*faicon:([^\*]+)\*',
                    r'<i class="fas fa-\g<1>"></i>', line)

    def collapsable_headers(self, html_source):
        collapsable_id = 0
        lines = html_source.split('\n')

        for i in range(len(lines)):
            m = re.match(r'\s*<h([0-9])>\^(.*)</h[0-9]>', lines[i])

            if m:
                collapsable_id += 1

                h_level = int(m.groups()[0])
                h_text = m.groups()[1]


                link = f'<a data-toggle="collapse" href="#collapse{collapsable_id}" role="button" aria-expanded="true" aria-controls="collapse{collapsable_id}">'
                icon = '<i class="fas fa-caret-down text-secondary"></i>'
                lines[i] = f'{link}\n<h{h_level}>{h_text}    {icon}</h{h_level}>'
                lines[i] += '\n</a>'

                lines[i] += f'<div class="collapse" id="collapse{collapsable_id}">'
                for j in range(i+1, len(lines)):
                    m2 = re.match(r'\s*<h([0-9])>(.*)</h[0-9]>', lines[j])
                    if m2:
                        if int(m2.groups()[0]) > h_level:
                            continue

                        lines[j-1] = lines[j-1] + '\n</div>'
                        i = j
                        break
                    if j == len(lines) - 1:
                        lines[j] += '</div>'

        return '\n'.join(lines)


    def process_links(self, line):
        # links, including images
        raw_links = re.findall(r'(.?\[[^]^)]+\]\([^)]+\))', line)

        for raw_link in raw_links:
            link = Link(raw_link)

            # external wiki links to normal links
#             if link.type_wiki:
#                 # TODO it's a hack
#                 line = link.make_wiki_links(self.base_url, line)

            if link.type_md and not link.type_wiki:
                # generate site, and then update link

                site = Site(self.base_url, self.output_dir, self.name)
                site.generate(os.path.join(self.mdfile.dir, link.destination),
                              self.template_env, self.bread_crums)
                line = link.update_destination(line,
                                        Site.PATH_HASH[site.mdfile.abs_path])

                line = link.destination_to_html(line)
                self.children.append(link.destination)

            line = link.copy_resources(line, self.resources_dir, self.base_url,
                                       self.mdfile.dir)

        return line


    def remove_stuff_in_md(self):
        # GLOBAL stuff:

        #remove html comments
        self.out_md_file = re.sub(r'<!--[\s\S]*?-->', '', self.out_md_file)

        # remove taskwariow hashes from task lists
        self.out_md_file = re.sub(r'(\* \[.\][^#]+)#.+', r'\g<1>', self.out_md_file)

        # remove taskwiki viewports
        self.out_md_file = re.sub(r'(#+[^\|\n]+)\|.+', r'\g<1>', self.out_md_file)


    def get_bread_crums(self, bread_crums):
#         bc_path = os.path.join(self.base_url, self.mdfile.dir,
#                                self.mdfile.basename_no_ext + '.html')
        bread_crums += ' / '
        bread_crums += f'<a style="color: #6668E6;" href="{self.out_filename_html}"> ' \
                       f'{self.mdfile.basename_no_ext}</a>'
        return bread_crums



    def get_cover(self):
        cover = ''
        if self.mdfile.cover_path:
            cover_link = Link(description="cover",
                              destination=self.mdfile.cover_path)
            cover_link.type_img = True
            cover_link.copy_resources("", self.resources_dir, self.base_url,
                                      self.mdfile.dir)
            cover = cover_link.destination
        return cover


    def change_checklist_icons(self, html_source):
        html_source = re.sub(r'\[X\]',
                                  r'<i class="fas fa-check-square"></i>',
                                  html_source)
        html_source = re.sub(r'\[\s\]',
                             r'<i class="fas fa-square"></i>', html_source)
        return html_source


    def remove_yaml_premable(self, md_text):
        return re.sub('^---\n([\s\S]*?)\n---', '', md_text)



    def generate(self, mdfile_path, template_env, bread_crums = ""):

        self.mdfile = MdFile(mdfile_path)
#         print(self.mdfile.content)
        self.mdfile.exec_embeded_scripts()
        self.mdfile.insert_files()
        self.mdfile.remove_percent_comments()

        if self.mdfile.abs_path in Site.PROCESSED_FILES:
            return


        # generate new name
        if len(Site.PROCESSED_FILES) == 0:
            self.out_filename_md = 'index.md'
        else:
            self.out_filename_md = hash_filename(self.mdfile.abs_path)
        self.out_filename_html = change_file_ext(self.out_filename_md, "html")

#         if len(Site.PROCESSED_FILES) == 0:
#             Site.INDEX_PAGE = change_file_ext(out_filename, "html")

        # save to dictionary
        Site.PATH_HASH[self.mdfile.abs_path] = self.out_filename_md
        Site.PROCESSED_FILES.append(self.mdfile.abs_path)
        Site.PROCESSED_FILE_NAMES.append(self.mdfile.basename)

        self.template_env = template_env
        self.bread_crums = self.get_bread_crums(bread_crums)

        # line by line stuff
        for line in self.mdfile.content.split('\n'):
            if not line:
                self.out_md_file += "\n"
                continue
            line = self.process_links(line)
            line = self.faicons(line)
            self.out_md_file += line + '\n'

        self.remove_stuff_in_md()

        if self.mdfile.bibliography != '':
            self.out_html_file = pypandoc.convert_text(self.out_md_file, 'html',
                                                       format='md',
                                                       extra_args=['--citeproc'])
        else:
            self.out_md_file = self.remove_yaml_premable(self.out_md_file)
            self.out_html_file = markdown.markdown(self.out_md_file,
                    extensions=['markdown.extensions.extra'])


        page_template = template_env.get_template('site.html')
        html_source = page_template.render(
                bread_crums=self.bread_crums,
                base_url=self.base_url,
                mdfile=self.out_md_file,
                html_content=self.out_html_file,
                name=self.name,
                title=self.mdfile.title,
                cover=self.get_cover())


        html_source = self.collapsable_headers(html_source)
        html_source = self.change_checklist_icons(html_source)

        html_file = open(os.path.join(self.output_dir,
                         self.out_filename_html),
                         'w')
        html_file.write(html_source)
        html_file.close()


