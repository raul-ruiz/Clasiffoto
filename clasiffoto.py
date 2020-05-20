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
        print(Fore.RED+ 'An error ocurred accessing EXIF data for ' + ruta)
    return info



def getFolderImages(path):
    fotos = []
    _extensions =  ["jpg","jpeg","JPG","JPEG","HEIC","NEF"]
    #Loop at folder content
    for file in os.listdir(path):
        #Check extension to process
       # if file.endswith("jpg") or file.endswith("jpeg") or file.endswith("HEIC") or file.endswith("JPG") or file.endswith("JPEG"): 
        if file.endswith(tuple(_extensions)):
            fotos.append(file)
    return fotos


def banner():
    print("\n" + 
        Fore.WHITE + " Clasiffoto " + Fore.RED + "raul.ruiz" + Fore.BLUE
    
    )

def moveFile(path,year,model,image):
    # Check if year and model could be calculated
    if (not(year) or not(model)):
        print(Fore.RED + ' => could not be moved as there is no EXIF info')       
    else:
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
        print("Dest file " + destinationfile)
        """destination = path + '//' + year + '//' +  model + '//' + images
        shutil.move(source,destination)"""
        if os.path.exists(destinationfile):
            print(Fore.LIGHTRED_EX + ' => not moved: file already exist' )
        else:
            shutil.move(sourcefile,destinationfile)
            print(Fore.GREEN + ' => moved to ' + destinationfile)


def processFolder(path):
    #Obtain images from folder
    images = getFolderImages(path)
    for image in images:
     
        imageInfo = getPicInfo(path+"/"+image)
      
        # Filter by year if specified
      
        if ((not args['year'])  or (args['year'] == imageInfo["year"])):
            
            print(Fore.WHITE + image , Fore.GREEN  + imageInfo["model"] , Fore.YELLOW + imageInfo["year"], Fore.LIGHTYELLOW_EX + imageInfo["resx"] +'x'+ imageInfo["resy"] ,Fore.LIGHTYELLOW_EX + 'W:'+imageInfo["sizex"],Fore.LIGHTYELLOW_EX + 'H:'+imageInfo["sizey"] ,sep=' ')
            if (args['generate']):
                #Move file
                moveFile(path,imageInfo["year"],imageInfo["model"],image)



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
    
    # Execute the parse_args() method
    args = vars(argparser.parse_args())
   
   
    # 
    if not os.path.isdir(args['Path']):
        print('The path specified does not exist')
        sys.exit()
    processFolder(args['Path'])

 