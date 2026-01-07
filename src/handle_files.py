import os
import shutil

'''
Write a recursive function that copies all the contents from a source directory to a destination directory 
(in our case, static to public)
- It should first delete all the contents of the destination directory (public) to ensure that the copy is clean.
- It should copy all files and subdirectories, nested files, etc.
- I recommend logging the path of each file you copy, so you can see what's happening as you run and debug your code.
'''

#delete the contents of public library;
print(os.listdir("."))

