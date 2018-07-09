import xml.etree.ElementTree
import urllib.request
import frontmatter

import sys
import os
import shutil
from io import BytesIO
import glob

e = xml.etree.ElementTree.parse('wordpress-xml/Posts-Export-2018-July-09-0915.xml').getroot()

def download_images():
    for each in e.findall('post'):
        title = each.find('Title')
        featured_image_url =  each.find('ImageFeatured')
        session_id =  each.find('_sessionID')
        
        if featured_image_url.text is not None:
            if session_id.text is not None:
                filename = session_id.text
            elif title.text is not None:
                filename = title.text.replace(" ", "").replace(":", "-").replace("/","-")
            else:
                filename = "Test"
            if featured_image_url.text:
                extension = "." + featured_image_url.text.split(".")[-1]
            else:
                extension = ".jpg"
                
            print("Downloading {0} to {1}".format(featured_image_url.text, "outputImages/" + filename + extension))
            urllib.request.urlretrieve(featured_image_url.text, "outputImages/" + filename + extension)
            


def retreive_list_of_uids_and_featured_images():
    list_of_posts = []
    for each in e.findall('post'):
        title = each.find('Title')
        featured_image_url =  each.find('ImageFeatured')
        session_id =  each.find('_sessionID')
        if featured_image_url.text is not None:
            if session_id.text is not None:
                filename = session_id.text
            elif title.text is not None:
                filename = title.text.replace(" ", "").replace(":", "-").replace("/","-")
            if featured_image_url.text:
                extension = "." + featured_image_url.text.split(".")[-1]
            else:
                extension = ".jpg"
            actual_filename = filename + extension
            if title.text is not None:
                title.text = title.text
                list_of_posts.append([title.text, actual_filename])
            elif session_id.text is not None:
                list_of_posts.append([title.text, actual_filename])    

    print(list_of_posts)
    return(list_of_posts)
    
    
def get_blog_posts(my_directory):
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
    
def add_featured_images_to_blog_posts(uids, blog_posts):
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
                    
    print("{0} posts to be changed!".format(count))
                
if __name__ == "__main__":
    
    uids = retreive_list_of_uids_and_featured_images()
    print(uids)
    blog_posts = get_blog_posts("/home/kyle.kirkby/Websites/connect.linaro.org/test_posts/")
    print("{0} blog posts found!".format(len(blog_posts)))
    result = add_featured_images_to_blog_posts(uids, blog_posts)
    
    if result:
        print("Hoorah Images added succuessfully")
    else:
        print("Images were not addeed successfully")
    
    
    
    
    