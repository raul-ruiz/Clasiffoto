# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
Clasiffoto 18/15/2020


"""
__author__="raul.ruiz"

import exifreader
from colorama import Fore, init
import sys
import os
import argparse
import shutil

def getPicInfo(ruta):
    info = {'model':'','year':'','resx':'','resy':'','sizex':'','sizey':''}
    # Open image (binary mode)
    f = open(ruta, 'rb')

    # Returns a dictionary with the selected tags
    try:
        tags = exifreader.process_file(f)
       
        for tag in tags.keys():
            if tag == 'Image Model':
                #Replace / by - in case the model name has a / (to avoid considering as folder)
                info['model'] = str(tags[tag]).replace('/','-')
                
            if tag == 'EXIF DateTimeOriginal':
                info['year'] = str(tags[tag])[:4]

            if tag == 'Image XResolution':
                info['resx'] = str(tags[tag])

            if tag == 'Image YResolution':
                info['resy'] = str(tags[tag])
            

            if tag == 'EXIF ExifImageWidth':
                info['sizex'] = str(tags[tag])

            if tag == 'EXIF ExifImageLength':
                info['sizey'] = str(tags[tag])



    except OSError:
        info = {'model':'','year':'','resx':'','resy':'','sizex':'','sizey':''}
    return info



def getFolderImages(path):
    fotos = []
    _extensions =  ["jpg","jpeg","JPG","JPEG","HEIC","NEF"]
    #Loop at folder content
    for file in os.listdir(path):
        #Check extension to process
        if file.endswith(tuple(_extensions)):
            fotos.append(file)
    return fotos


def banner():
    print("\n" + 
        Fore.WHITE + " Clasiffoto " + Fore.RED + "raul.ruiz" + Fore.BLUE
    
    )

def moveFile(path,year,model,image):
  
    destinationpath = os.path.join(path,year)
        
    # Check if there is already a folder for the year. Otherwise, create
    if not (os.path.isdir(destinationpath)):
        os.mkdir(destinationpath)

    #Check if there is already a folder for the model. Otherwise, create
    destinationpath = os.path.join(destinationpath,model)
    if not (os.path.isdir(destinationpath)):
        os.mkdir(destinationpath)



    #Move file
    sourcefile = os.path.join(path ,image)
    destinationfile = os.path.join(destinationpath,image)
    if os.path.exists(destinationfile):
        return 'E', 'Not moved: file ' + destinationfile +' already exist'
    else:
        shutil.move(sourcefile,destinationfile)
        return 'S', 'Moved to ' + destinationfile
        
def processFolder(path):
    #Obtain images from folder
    images = getFolderImages(path)
    for image in images:
     
        imageInfo = getPicInfo(path+"/"+image)
      
        # Filter by year if specified
        if ((not args['year'])  or (args['year'] == imageInfo["year"])):
            

            if (not imageInfo["year"] or not imageInfo["model"]):
                 printPicStatus(image,imageInfo,'E','No EXIF info obtained')
            else:
                if (args['generate']):
                    #Move file
                    response,text = moveFile(path,imageInfo["year"],imageInfo["model"],image)
                    
                    #Print depending on onlyerrors flag to hide success
                    if (not args['onlyerrors'] or ( args['onlyerrors']  and response != 'S') ):
                        printPicStatus(image,imageInfo,response,text)
    
                # If not generating structure, just print if unless onlyerrors
                
                else:
                    if (not args['onlyerrors']):
                        printPicStatus(image,imageInfo,'','')




def printPicStatus(image,imageInfo,kind,text):
        
    print(Fore.WHITE + image , Fore.GREEN  + imageInfo["model"] , Fore.YELLOW + imageInfo["year"], Fore.LIGHTYELLOW_EX + 'Res X:' + imageInfo["resx"] + ' Res Y:' + imageInfo["resy"] , Fore.YELLOW + 'W:' + imageInfo["sizex"],Fore.YELLOW + 'H:'+imageInfo["sizey"] ,sep=' ',end=' ')
    if (kind == 'S'):
        print(Fore.WHITE + ' => ',Fore.GREEN + text)
        return
    if (kind == 'W'):
        print(Fore.WHITE + ' => ',Fore.YELLOW + text)
        return
    if (kind == 'E'):
        print(Fore.WHITE + ' => ',Fore.RED + text)
        return
    print('')

if __name__ == "__main__":
    #Control arguments with parser
    argparser = argparse.ArgumentParser(description='Process pics folder based on Exif data')

    # Add the arguments
    argparser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='Path to the folder that contains images')
    argparser.add_argument('--year', type=str, required=False, action='store', help='Only consider pics with especific year in exif')                       
    argparser.add_argument('--generate', required=False, action='store_true', help='Generate folders for years and camera model')                       
    argparser.add_argument('--onlyerrors', required=False, action='store_true', help='Show only errors')                       
    
    # Execute the parse_args() method
    args = vars(argparser.parse_args())
   
   
    # 
    if not os.path.isdir(args['Path']):
        print('The path specified does not exist')
        sys.exit()
    processFolder(args['Path'])

 