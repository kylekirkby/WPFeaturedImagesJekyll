import xml.etree.ElementTree
import urllib.request
import json
import frontmatter
import sys
import os
import shutil
from io import BytesIO
import glob
import re 
import argparse
import subprocess

e = xml.etree.ElementTree.parse('xml/Member-Export-2018-August-09-1324.xml').getroot()

class TermColours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKCYAN = '\033[36m'
    WARNING = '\033[93m'
    LIGHT_GREY = '\033[37m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class StaticWebsiteUtility:

    """
    Python command line tool to carry out useful tasks for modifying files in our Jekyll Static Websites.
    """

    def __init__(self):
        # Defaults
        self.proxies = {}
        self.destination_folder = "output/"
        self.verbose = False
        self.out_path_generated = False
        self.out_path = ""
        self.full_path_to_image = ""
        # Parser
        self.parser = argparse.ArgumentParser(description="Linaro Jekyll Static Website Python Utility")
        # Setup the parser object
        self.setup_parser()
        # Get the args
        self.args = self.parser.parse_args()
        if self.args.task and self.args.site:
            print("Performing {0} task for {1}...".format(self.args.task, self.args.site))
        # Setup Args and Program
        # self.setup()
        # Run Main Method
        self.main()

    def output_warning(self, message):
        return(TermColours.WARNING + message + TermColours.ENDC)

    def output_lg(self, message):
        return(TermColours.LIGHT_GREY + message + TermColours.ENDC)

    def output_fail(self, message):
        return(TermColours.FAIL + message + TermColours.ENDC)

    def output_ok_green(self, message):
        return(TermColours.OKGREEN + message + TermColours.ENDC)

    def output_ok_blue(self, message):
        return(TermColours.OKBLUE + message + TermColours.ENDC)

    def output_ok_cyan(self, message):
        return(TermColours.OKCYAN + message + TermColours.ENDC)

    def success(self, message):
        return(TermColours.OKGREEN + "SUCCESS: " + message + TermColours.ENDC)

    def warning(self, message):
        return(TermColours.OKCYAN + "WARNING: " + message + TermColours.ENDC)

    def failed(self, message):
        return(TermColours.FAIL + "FAILED: " + message + TermColours.ENDC)

    def status(self, message):
        return(TermColours.OKCYAN + "STATUS: " + message + TermColours.ENDC)

    # Setup the Argument Parser
    def setup_parser(self):
        # Required Positional Arguments
        required_arguments_group = self.parser.add_argument_group('Required Arguments')
        required_arguments_group.add_argument(
            "site", help="The path to the root of the Static Jekyll Website.")
        required_arguments_group.add_argument(
            "task", help="The task that you wish to perform e.g $ util.py /home/kyle.kirkby/Websites/connect.linaro.org/ slideshare-embed ")
        # # Optional Arguments
        # optional_arguments_group = self.parser.add_argument_group('')
        # Flags
        flag_arguments_group = self.parser.add_argument_group('Flags')
        flag_arguments_group.add_argument(
            "-v", "--verbose", dest="verbose", help="Verbose output of the script")

    def download_images(self):
        for each in e.findall('post'):
            title = each.find('Title')
            featured_image_url =  each.find('ImageFeatured')
                        
            if featured_image_url.text is not None:
                # Choose a suitable image name
                if title.text is not None:
                    filename = title.text
            
                # Get the file extension
                if featured_image_url.text:
                    extension = "." + featured_image_url.text.split(".")[-1]
                else:
                    extension = ".jpg"

                print("Downloading {0} to {1}".format(featured_image_url.text, "outputImages/" + filename + extension))
                urllib.request.urlretrieve(featured_image_url.text, "outputImages/" + filename + extension)
                
    def retreive_list_of_uids_and_featured_images(self):
        list_of_posts = []
        for each in e.findall('post'):
            title = each.find('Title')
            featured_image_url =  each.find('ImageFeatured')
            permalink =  each.find('Permalink')
            
            if featured_image_url.text is not None:
                # Choose a suitable image name
                if title.text is not None:
                    filename = title.text
            
                # Get the file extension
                if featured_image_url.text:
                    extension = "." + featured_image_url.text.split(".")[-1]
                else:
                    extension = ".jpg"

                actual_filename = filename + extension
                if title.text is not None:
                    title.text = title.text
                    list_of_posts.append([title.text, actual_filename])
                elif permalink.text is not None:
                    list_of_posts.append([title.text, actual_filename])    

        print(list_of_posts)
        return(list_of_posts)
        
        
    def get_blog_posts(self, my_directory):
        types = [".md",".markdown",".mdown"]
        
        if my_directory.endswith("/"):
            directory_name = my_directory.split("/")[-2]
        else:
            directory_name = my_directory.split("/")[-1]
                
        # Loop through and find all markdown files
        markdown_files = []
        for t in types:
            for markdown_file in glob.iglob('{0}/**/*{1}'.format(my_directory,t), recursive=True):
                markdown_files.append(markdown_file)
        return markdown_files
        
    def add_featured_images_to_blog_posts(self, uids, blog_posts):
        count = 0
        # Loop through all the markdown posts in the directory
        for post in blog_posts:
            front_matter = frontmatter.loads(open(post,"r").read())
            # Get featured image from uids
            for uid in uids:
                if uid[0] == front_matter["title"]:
                    print("Match")
                    if "featured_image_name" in front_matter.keys():
                        print(front_matter["featured_image_name"])
                    else:
                        count += 1
                        print("No Image found - adding new image....")
                        front_matter["featured_image_name"] = uid[1]
                        with open(post,"w") as changed_file:
                            changed_file.writelines(frontmatter.dumps(front_matter))
                            # frontmatter.dump(front_matter, changed_file)
                            print("{0} changed for {1}".format(str(uid[1]), front_matter["featured_image_name"]))
                            
                    count += 1
                    print("No Image found or updating front matter")
                    front_matter["image"] = {"name": uid[1],
                                            "path": "/assets/images/speakers/" + uid[1],
                                            "featured": True
                                            }
                    with open(post,"w") as changed_file:
                        changed_file.writelines(frontmatter.dumps(front_matter))
                        # frontmatter.dump(front_matter, changed_file)
                        print("{0} changed for {1}".format(str(uid[1]), front_matter["image"]))


    def get_slideshare_embed_url(self, url):
        api_url = "http://www.slideshare.net/api/oembed/2?url={0}&format=json".format(url)
        print("API CALl: {0}".format(api_url))
        with urllib.request.urlopen(api_url) as url:
            data = json.loads(url.read().decode())
            slideshare_id = data['slideshow_id']
            embed_url = "//www.slideshare.net/slideshow/embed_code/" + str(slideshare_id)
        return embed_url

    def add_slideshare_embed_urls(self, blog_posts):
        count = 0
        # Loop through all the markdown posts in the directory
        for post in blog_posts:
            front_matter = frontmatter.loads(open(post,"r").read())
            # Get Slideshare URL from each blog post and add the embed url
            try:
                slideshare_url =  front_matter["slideshare_presentation_url"]
                if slideshare_url == "None":
                    pass
                else:
                    #resource_url =  front_matter["link"]
                    embed_url = get_slideshare_embed_url(slideshare_url)
                    if front_matter["slideshare_embed_url"] == embed_url:
                        pass
                    else:
                        front_matter["slideshare_embed_url"] = embed_url
                        with open(post,"w") as changed_file:
                            changed_file.writelines(frontmatter.dumps(front_matter))
                            # print("{0} changed for {1}".format(embed_url, post))
                        count += 1
            except Exception as e:
                print(e)
                pass
                
        print("{0} posts changed!".format(count))

        return True
    
    def add_permalinks(self, blog_posts, permalink):

        count = 0
        # Loop through all the markdown posts in the directory
        for post in blog_posts:
            front_matter = frontmatter.loads(open(post,"r").read())
            # Get Slideshare URL from each blog post and add the embed url
            front_matter["permalink"] = "/speaker/:title/"
            with open(post,"w") as changed_file:
                changed_file.writelines(frontmatter.dumps(front_matter))
            count += 1
                
        print("{0} posts changed!".format(count))

        return True

    def add_layout(self, blog_posts, layout):

        count = 0
        # Loop through all the markdown posts in the directory
        for post in blog_posts:
            front_matter = frontmatter.loads(open(post,"r").read())
            # Get Slideshare URL from each blog post and add the embed url
            front_matter["layout"] = layout
            with open(post,"w") as changed_file:
                changed_file.writelines(frontmatter.dumps(front_matter))
            count += 1
                
        print("{0} posts changed!".format(count))

        return True

    def add_category(self, blog_posts, category):
        count = 0
        # Loop through all the markdown posts in the directory
        for post in blog_posts:
            front_matter = frontmatter.loads(open(post,"r").read())
            # Get Slideshare URL from each blog post and add the embed url
            front_matter["categories"] = category
            with open(post,"w") as changed_file:
                changed_file.writelines(frontmatter.dumps(front_matter))
            count += 1
                
        print("{0} posts changed!".format(count))

        return True

    def main(self):
        # self.download_images()
        uids = self.retreive_list_of_uids_and_featured_images()
        print(uids)
        blog_posts = self.get_blog_posts("/home/kyle.kirkby/Websites/connect.linaro.org/site/_posts/speaker/")
        print("{0} blog posts found!".format(len(blog_posts)))
        result = self.add_featured_images_to_blog_posts(uids, blog_posts)
        # result = self.add_slideshare_embed_urls(blog_posts)
        # result = self.add_permalinks(blog_posts, "/speaker/:title/")
        # result = self.add_layout(blog_posts, "speaker-post")
        # result = self.add_category(blog_posts, "speaker")
        
        if result:
            print("Script completed successfully.")
        else:
            print("Script failed.")
                
if __name__ == "__main__":

    utility = StaticWebsiteUtility()
    
    
    
    