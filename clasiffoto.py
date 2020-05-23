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
from tabulate import tabulate

def getPicInfo(ruta):
    info = {'model':'','year':'','resx':'','resy':'','sizex':'','sizey':'','size':''}
    # Open image (binary mode)
    f = open(ruta, 'rb')


    #info['filename'] = os.path.splitext(os.path.basename(ruta))[0].upper()
    
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

        #Get filesize
        info['size']  = str(round(( os.stat(ruta).st_size / 1024 ) / 1024,2))

    except OSError:
        info = {'model':'','year':'','resx':'','resy':'','sizex':'','sizey':'','size':''}
    return info



def getFolderImages(path):
    fotos = []
    _extensions =  ["PNG","png","MOV","mov","NEF",'nef',"jpg","jpeg","JPG","JPEG","HEIC","NEF"]
    #Loop at folder content
    for file in os.listdir(path):
        #Check extension to process
        if file.endswith(tuple(_extensions)):
            fotos.append(str(file).upper())
    return fotos


def banner():
    print("\n" + 
        Fore.WHITE + " Clasiffoto " + Fore.RED + "raul.ruiz" + Fore.BLUE
    
    )

def moveFileNewFolder(path,year,model,image):
  
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

def moveFileWithPath(source,destination ,image):
  
    sourcefile = os.path.join(source,image)
    destinationfile = os.path.join(destination,image)
    
    #Move file
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
                    response,text = moveFileNewFolder(path,imageInfo["year"],imageInfo["model"],image)
                    
                    #Print depending on onlyerrors flag to hide success
                    if (not args['onlyerrors'] or ( args['onlyerrors']  and response != 'S') ):
                        printPicStatus(image,imageInfo,response,text)
    
                # If not generating structure, just print if unless onlyerrors
                
                else:
                    if (not args['onlyerrors']):
                        printPicStatus(image,imageInfo,'','')



def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('Please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False 
    # Source: http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/

def printHeader(text):
    print(Fore.BLUE + text)
    

def printPicStatus(image,imageInfo,kind,text):
        
    print(Fore.WHITE + image , Fore.GREEN  + imageInfo["model"] , Fore.YELLOW + imageInfo["year"], Fore.LIGHTYELLOW_EX + 'Res X:' + imageInfo["resx"] + ' Res Y:' + imageInfo["resy"] , Fore.YELLOW + 'W:' + imageInfo["sizex"],Fore.YELLOW + 'H:'+imageInfo["sizey"],Fore.YELLOW + 'Size: '+imageInfo["size"] ,sep=' ',end=' ')
        
    if (kind == 'S'):
        print(Fore.WHITE + ' => ',Fore.GREEN + text)
        return
    if (kind == 'W'):
        print(Fore.WHITE + ' => ',Fore.YELLOW + text)
        return
    if (kind == 'E'):
        print(Fore.WHITE + ' => ',Fore.RED + text)
        return
    if (kind == 'I'):
        print('')
        return
    print('')


def compareFolder(source,destination):
    sourceImages = getFolderImages(source)
    destinationImages = getFolderImages(destination)

    # Check images that exist only on source or destination folder
    onlySource = list(set(sourceImages)-set(destinationImages))
    onlyDestination = list(set(destinationImages)-set(sourceImages))
    common = list(set(destinationImages) & set(sourceImages))
    #Check common using only filename without extension
    #notsureifcommon = list(set(map(lambda x: os.path.splitext(x)[0].upper(),sourceImages)) & set(map(lambda x: os.path.splitext(x)[0].upper(),destinationImages)))
     
    #Print results

    if common and not args['onlyonsource'] and not args['onlyondestination']:
        printHeader('Image that exist on both source and destination folder')
        report = []
        for image in common:
            imgInfoDest = getPicInfo(destination+"/"+image)
            imgInfoSource = getPicInfo(source+"/"+image)
            report.append( [image] + list(imgInfoSource.values()) + list(imgInfoDest.values()))
        print(tabulate(report,headers=['Image','Src.Model','Year','ResX','ResY','Width','Height','Size','Name','Dst.Model','Year','ResX','ResY','Width','Height','Size','Name']))

    if onlySource and not args['onlycommon'] and not args['onlyondestination']:
        printHeader('Image only exist on source folder:'+source)
        for image in onlySource:
            imgInfo = getPicInfo(source+"/"+image)
            if (not imgInfo["year"] or not imgInfo["model"]):
                printPicStatus(image,imgInfo,'E','No EXIF info obtained')
            else:
                printPicStatus(image,imgInfo,'I','')

    if onlyDestination and not args['onlycommon'] and not args['onlyonsource']:
        printHeader('Image only exist on destination folder: '+destination)
        for image in onlyDestination:
            imgInfo = getPicInfo(destination+"/"+image)
            if (not imgInfo["year"] or not imgInfo["model"]):
                printPicStatus(image,imgInfo,'E','No EXIF info obtained')
            else:
                printPicStatus(image,imgInfo,'I','')



def moveFolder(source,destination):

    if (confirm(prompt='Do you want to move the missing files in destination folder?',resp=False)):
        sourceImages = getFolderImages(source)
        destinationImages = getFolderImages(destination)

        # Check images that exist only on source  
        onlySource = list(set(sourceImages)-set(destinationImages))


        for image in onlySource:
            imgInfo = getPicInfo(source+"/"+image)
            response,text = moveFileWithPath(source,destination, image)
                    
            #Print depending on onlyerrors flag to hide success
            if (not args['onlyerrors'] or ( args['onlyerrors']  and response != 'S') ):
                printPicStatus(image,imgInfo,response,text)

            



if __name__ == "__main__":
    #Control arguments with parser
    argparser = argparse.ArgumentParser(description='Process pics folder based on Exif data')

    # Add the arguments
    argparser.add_argument('path',
                       metavar='path',
                       type=str,
                       help='Path to the folder that contains images')
    argparser.add_argument('--year', type=str, required=False, action='store', help='Only consider pics with especific year in exif')                       
    argparser.add_argument('--comparedest', type=str, required=False, action='store', help='Compare with pics in a destination path')                       
    argparser.add_argument('--movedest', type=str, required=False, action='store', help='Compare with pics in a destination path and move required ones')                       
    argparser.add_argument('--generate', required=False, action='store_true', help='Generate folders for years and camera model')                       
    argparser.add_argument('--onlyerrors', required=False, action='store_true', help='Show only errors')                       
    argparser.add_argument('--onlycommon', required=False, action='store_true', help='Show only common images')                       
    argparser.add_argument('--onlyonsource', required=False, action='store_true', help='Show only images that only exists on source')                       
    argparser.add_argument('--onlyondestination', required=False, action='store_true', help='Show only images that only exists on destination')                       
                       
    
    # Execute the parse_args() method
    args = vars(argparser.parse_args())
   
   
    # 
    if not os.path.isdir(args['path']):
        print('The path specified does not exist')
        sys.exit()
    # In case there is no comparison action, processfolder is launched    
    if not args['comparedest'] and not args['movedest']:
        processFolder(args['path'])
    else:
        if args['comparedest'] :
            compareFolder(args['path'],args['comparedest'])
        else:
            if args['movedest']:
                moveFolder(args['path'],args['movedest'])
 