#!/usr/bin/env python
# coding: utf-8

# # ssg.ipynb
# 
# Here is the simple static site generator, ecrit en procrastination.
# 
# Note that this README *isn't* a traditional readme. This is the 👉**ENTIRE SOURCE CODE**👈, exported from a jupyter notebook.
# 
# ### Architecture: 
# 1. Have a `posts` directory with some text files, in a custom format
# 2. Parse the custom format (called SparkDown)
# 3. Have `invariants` directory with some constant boilerplate
# 4. Link to the correct `invariant` templates based on metadata in the SparkDown
# 5. Render and put the output into a `build` folder
# 
# ### The SparkDown format
# 
# This will be a markdown-inspired format, written from scratch primarily for 
# pedagogy, simplicity, and escape from heteronomy.
# 
# There are two types of parsing:
# 
# - Line based: Choses the `mode`
# - Inner line based: Modifies the line, according to the `mode`
# 
# Modes are chosed with a [sigil](https://en.wikipedia.org/wiki/Sigil_(computer_programming))
# at the beginning of a line. 
# 
# For instance, `# Hello world` sets the `mode` to `header` with the `#` sigil.
# 
# ### For obsidian support, we will also read .md files

# In[1]:


some_text = """
$ template: index

# Hello welcome to [my blog](https://myblog.com)

Welcome to my cool blog! It can even link. It can do [[internal links]].
It can even do images like {this.jpg}

I wrote it in my own [markup format](https://google.com) it's not [very good](https://something.com)! but it's a start!
"""


# ### Utils:

# In[2]:


def eat(text):
    """
    Eats the first element of the array.
    
    Returns empty if nothing left
    """
    try:
        text.pop(0)
    except IndexError:
        pass
    return text

def linkify(text):
    """
    Turn a title into a link slug
    
    ex. "whats going on?" -> "whats_going_on"
    """
    return text.replace(" ", "_").replace("?","")


# ### Mode parsers:
# 
# Mode parsers work like the following: 
# 
# We take two parameters `rest` and `post_so_far` and are expected
# to return them, modified, at the end of the function.
# 
# `rest` and the array of *lines* in the original text
# 
# `post_so_far` is a *string* of the current output
# 
# Currently we have two modes: 
# 
# - sigil `#`:`header` mode wraps the line in a header
# - sigil `$`:`meta` a key:value pair for metadata in the following format:
#     - `$<SPACE><KEY>:<SPACE><VALUE>`

# In[3]:


def parse_header(rest, post_so_far, level=1):
    """
    Parse a header at the beginning of the line
    
    # Like this
    """
    curr_line_without_hash = rest[0][level:]
    header = f"<h{level}>{parse_line(curr_line_without_hash)}</h{level}> \n"
    post_so_far += header
    
    return (eat(rest), post_so_far)

def parse_meta(rest, metadata):
    """
    Parse a metadata line
    
    Like this: 
    $ key: value
    
    The spaces are not optional.
    """
    curr_line = rest.pop(0)
    curr_line = curr_line.split(" ")

    key, value = curr_line[1], curr_line[2]
    key = key[:key.find(":")]
    
    metadata[key] = value
    return (rest, metadata)

def parse_nothing(rest, post_so_far):
    """
    Parse a simple 'nothing' block. These should be squeezed together.
    
    To do this, we look ahead.
    """
    if (len(rest) == 1):
        return (eat(rest), post_so_far)
    
    lookeahead = rest[1]
    if rest == "":
        return (eat(rest), post_so_far)
    else:
        post_so_far += "<p></p>\n"
        return (eat(rest), post_so_far)

def parse_generic(rest, post_so_far):
    """
    Parse a generic text block
    """
    post_so_far += "<p>\n  "
    while(len(rest)):
        curr_line = rest[0]
        if curr_line == "":
            break
        
        post_so_far += f"{parse_line(curr_line)}\n"
        eat(rest)
    post_so_far += "</p>\n"
    
    return (eat(rest), post_so_far)


# ### Line Parsers:
# 
# Much in the same way the main parser parses *text* into *lines*, 
# the line parser splits the line into *words*, and calls the necessary parse function.

# In[4]:


class BacklinkSingleton():
    """
    Generic buffer to push backlinks onto.
    
    Singletons are dangerous in notebooks! Remember to clear
    """
    _title = ""
    backlinks = {}
    
    def __init__(self):
        return
    
    @classmethod
    def push(cls, data):
        if (data in cls.backlinks):
            cls.backlinks[data].add(cls._title)
        else:
            cls.backlinks[data] = set([cls._title])
        
    @classmethod
    def set_title(cls, data):
        cls._title = data
        
    @classmethod
    def clear(cls):
        cls._title = ""
        cls.backlinks = {}

def parse_line(line):
    """
    Parses a markup format
    """
    line_so_far = ""
    words = line.split(" ")
    rest = words
    
    while(len(rest)):
        curr_word = rest[0]
        mode = curr_word[0] if len(curr_word) else ""
        mode_peek = curr_word[1] if len(curr_word) > 1 else ""
        
        if (mode + mode_peek == "[["):
            rest, line_so_far = parse_wikilink(rest, line_so_far)
        elif (mode == "["):
            rest, line_so_far = parse_link(rest, line_so_far)
        elif (mode == "{"):
            rest, line_so_far = parse_image(rest, line_so_far)
        else:
            rest, line_so_far = parse_generic_word(rest, line_so_far)

    return line_so_far  

def parse_link(rest, line_so_far):
    """
    Parses a link, starts with a `[` character
    """
    word = rest.pop(0)
    while(word.find("]") == -1):
        word += " "
        word += rest.pop(0)
        
    inner_text, link = word.split("]")
    
    inner_text = inner_text[1:]
    last_right_paren = link.rfind(")")
    link, after_link = link[1:last_right_paren], link[last_right_paren+1:]
    
    line_so_far += f"<a class='outbound' href='{link}'>{inner_text}</a>{after_link} "
    return (rest, line_so_far) # Here we don't eat the rest, since we ate before

def parse_wikilink(rest, line_so_far):
    """
    Parses a wikilink style link (the kind like [[this]] format)
    """
    word = ""
    while(word.find("]") == -1):
        word += rest.pop(0)
        word += " "
        
    word = word[2:-3]
    BacklinkSingleton.push(word)
    quote = '"'
    line_so_far += f"<a onclick='getPage({quote}{linkify(word)}.html{quote})' class='internal'>{word}</a>"
    return (rest, line_so_far)

def parse_image(rest, line_so_far):
    """
    Parses an image link in the form {image.jpg} 
    
    I think this is a way nicer way than the markdown format
    """
    word = rest.pop(0)
        
    word = word[1:-1]
    line_so_far += f"<img class='imagelink' src='/{word}' />"
    return (rest, line_so_far)

def parse_generic_word(rest, line_so_far):
    """
    Just appends the word
    """
    word = rest[0]
    line_so_far += f"{word} "
    
    return (eat(rest), line_so_far)


# ### Complete parser:

# In[5]:


def parse_markup(text):
    """
    Parses a markup format.
    
    Markup is text and metadata, so this will return both.
    
    Also even though python passes dicts and list by reference, we
    make the re-assignment explicit to communicate what's happening.
    """
    post_so_far = ""
    metadata = {}
    lines = text.split("\n")
    rest = lines
    
    while(len(rest)):
        curr_line = rest[0]
        mode = curr_line[0] if len(curr_line) else ""
        mode_peek = curr_line[1] if len(curr_line) > 1 else ""

        if   (mode + mode_peek == "##"):
            rest, post_so_far = parse_header(rest, post_so_far, level=2)
        elif (mode == "#"):
            rest, post_so_far = parse_header(rest, post_so_far)
        elif (mode == "$"):  # This function is different as we don't change post_so_far
            rest, metadata = parse_meta(rest, metadata)
        elif (mode == ""):
            rest, post_so_far = parse_nothing(rest, post_so_far)
        else:
            rest, post_so_far = parse_generic(rest, post_so_far)

    return post_so_far, metadata


# In[6]:


# test parser

# parse_markup(some_text)


# # The `post` object
# 
# The posts will parsed into a `post` object, which the template evaluator will have available in it's context.
# 
# This object will have attributes such as: 
# 
#  - `title`: The title of the post. The file name.
#  - `content`: The content of the post
#  - `buffer`: An all-purpose buffer, so that the `exec` contexts can put output in

# In[7]:


class Post():
    """
    This class represents a single post, and will be given to the template object
    """
    
    def __init__(self, title, content, metadata):
        """
        Sets the title and content.
        """
        self.title = title
        self.content = content
        self.metadata = metadata
        self.backlinks = []
        self.buffer = ""
        
    def get_formatted_title(self):
        """
        Get the formatted title for the link
        """
        return linkify(self.title)
        
    
    def print(self, text, end="\n"):
        """
        Puts text content into the buffer
        """
        self.buffer += f"{text}{end}"
        
    def clear_buffer(self):
        """
        Clears the post object's buffer
        """
        self.buffer = ''


# # Our very own template syntax
# 
# It will work like the following
# 
# It is parsed as regular html until
# two colons are encountered `::`, at which point control is given to python.
# 
# To communicate input and output between the template python and the main python ssg, we will
# use the `buffer` in the `Post` object. To print to this buffer, we use `post.print`.
# 
# ```
# <p>
# ::
# post.print(post.content)
# ::
# </p>
# ```
# 
# If the directive "keep" is given, then both the code and it's output will be given, like a jupyternotebook cell.
# 
# ```
# <p>
# ::keep
# post.print(post.content)
# ::
# </p>
# ```
# will give
# ```
# <p>
# <div class="inputcode">
# post.print(post.content)
# </div>
# hello
# </p>
# ```

# In[8]:


def render_page(post, posts, template_name="blog", backlinks=None):
    """
    `post`: is the current post
    `posts`: is all the posts
    
    Renders a page according the template `template`,
    which needs to be in the `invariants` folder, and have the `.sdml` extension
    """
    with open(f"./invaraints/{template_name}.sdml") as file:
        template = file.read()
        
        post_so_far = ""
        lines = template.split("\n") # We don't want to keep the newline
        rest = lines
        
        while(len(rest)):
            curr_line = rest[0]
            
            if (curr_line == "::"):
                rest, post_so_far = parse_sdml_block(rest, post_so_far, post)
            elif (curr_line == "::keep"):
                rest, post_so_far = parse_sdml_block(rest, post_so_far, post, keep_code=True)
            else:
                rest, post_so_far = parse_sdml_generic(rest, post_so_far)
                
        return post_so_far
        
def parse_sdml_block(rest, post_so_far, post, keep_code=False):
    """
    Parses the sdml block with the current `post` context 
    """
    code = ""
    eat(rest)
    lookahead = rest.pop(0)
    while(lookahead != "::"):
        code += f"{lookahead}\n"
        lookahead = rest.pop(0)
        
    local_vars = {
        "post": post,
        "posts": posts,
        "linkify": linkify,
    }
    
    exec(code, None, local_vars)
    if keep_code:
        CODE_HEADER = '<div class="inputcode">\n'
        CODE_FOOTER = '</div>\n'
        post_so_far += f"{CODE_HEADER}{code}{CODE_FOOTER}"
    
    post_so_far += post.buffer
    post.clear_buffer()
    
    return (rest, post_so_far)

    
def parse_sdml_generic(rest, post_so_far):
    """
    Just returns the text, moving the pointer forward
    """
    post_so_far += f"{rest[0]}\n"
    return (eat(rest), post_so_far)


# # Find the files in the `posts` folder
# 
# Now we go one-by-one to every post in `posts` folder and convert them to html pages.
# 
# It needs to by of type `sd`

# In[9]:


import glob
from pathlib import Path


# In[10]:


def getbasename(path):
    return path.split("/")[-1][:-3]

def format_path_title(title):
    return replace_spaces_with_underscore(title.replace("?",""))


# In[11]:


if __name__ == "__main__":
    header = ""
    footer = ""

    with open("./invaraints/head.html") as headerfile:
        header = headerfile.read()

    with open("./invaraints/footer.html") as footerfile:
        footer = footerfile.read()

    Path("./build").mkdir(parents=True, exist_ok=True)
            
    print("Adding assets")
    for path in glob.iglob("./assets/*"):
        with open(path, "rb") as file:
            
            content = file.read()
            path_end = path.split("/")[-1]
            with open(f"./build/{path_end}", "wb") as new_file:
                new_file.write(content)
        print(f"{path} added")

    posts = []
    link_graph = {}
    for path in glob.iglob("./posts/*.*d"):
        with open(path) as file:
            post_text = file.read()
            title = getbasename(path)
            
            BacklinkSingleton.set_title(title)
            content, metadata = parse_markup(post_text)
            
            post = Post(title, content, metadata)
            posts.append(post)
    
    for post in posts:
        template = "blog" 
        if "template" in post.metadata:
            template = post.metadata['template']
            
        if post.title in BacklinkSingleton.backlinks:
            post.backlinks = BacklinkSingleton.backlinks[post.title]

        page_content = render_page(post, posts, template_name=template)
        post_html = f"{header}{page_content}{footer}"

        build_path = f"./build/{linkify(post.title)}.html"
        with open(build_path, "w") as outfile:
            outfile.write(post_html)
            print(f"Built {post.title} \033[94m => \033[0m {build_path}")
            
    BacklinkSingleton.clear()


# 

# In[ ]:





# In[ ]:




