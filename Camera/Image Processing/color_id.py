import cv2
import numpy as np

#Script for determining the percentage of each color using PIL and using
#RGB representation. When running in the command line, type the image file. Type
#True if you want to see the image after the filters are applied

def get_mask(image, lower_bound, upper_bound):
    threshold = cv2.inRange(image, lower_bound, upper_bound)
    mask = cv2.bitwise_and(image, image, mask=threshold)
    return cv2.bitwise_and(image, mask)


def part_1(image):
    color_range = {}
    #Figure out what the lower and upper bounds for each color should be
    color_range["blue"] = [(?,?,?), (?,?,?)]
    color_range["green"] = [(?,?,?), (?,?,?)]
    color_range["red"] = [(?,?,?), (?,?,?)]
    
    #Counter for amount of pixels of each color
    color_amount = {"red":0, "green":0, "blue":0}
        
    #PART 1: COLOR IDENTIFICATION
    #<YOUR CODE GOES HERE>
    
    
    
    
    total_pixels = image.shape[0] * image.shape[1]
    perc_red = color_amount["red"] / total_pixels
    perc_green = color_amount["green"] / total_pixels
    perc_blue = color_amount["blue"] / total_pixels
    
    return (color_range, perc_blue, perc_green, perc_red)



def part_2(image, image_HSV):
    #PART 2 TODO: Increase saturation, contrast, brightness, etc
    #<YOUR CODE GOES HERE>
    enhanced_image =  #Don't change the input images, store new enhanced image here
    
    return enhanced_image

    
    
#Main code that is being run
def color_id(image_file = 'test.jpg', show = False):
    folder_path = '' #Replace with the folder path for the folder in the
                     #Flat Sat Challenge with your name so you can view images
                     #on Github if you don't have VNC/X forwarding


    image = cv2.imread('images/' + image_file) #Converts image to numpy array in BGR format
    image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #Converts BGR image to HSV format
    
    color_range, perc_blue, perc_green, perc_red = part_1(image)
    
    print("The percentage of red is",round(100*perc_red,2),"%")
    print("The percentage of green is",round(100*perc_green,2),"%")
    print("The percentage of blue is",round(100*perc_blue,2),"%")
    

    blue_mask = get_mask(image, *color_range['blue'])
    green_mask = get_mask(image, *color_range['green'])
    red_mask = get_mask(image, *color_range['red'])
    
    #If the show flag is set to true, this will set up images to visualize the color ID.
    #Note: if you're on a windows machine and haven't set up X11 forwarding, 
    #this won't work. If show is set to False, the image masks will be stored to
    #the images/ folder
    if show:
        cv2.imshow('Blue Mask', blue_mask)
        cv2.imshow('Green Mask', green_mask)
        cv2.imshow('Red Mask', red_mask)
        
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        cv2.imwrite(folder_path + '/blue_mask.jpg', blue_mask)
        cv2.imwrite(folder_path + '/green_mask.jpg', green_mask)
        cv2.imwrite(folder_path + '/red_mask.jpg', red_mask)
        print('Image masks saved')
    
    #Uncomment when you want to work on part 2
    """
    enhanced_image = part_2(image, image_HSV)
    
    #Shows orginal image and enhanced image
    if show:
        cv2.imshow('Original Image', image) 
        cv2.imshow('Enhanced Image', enhanced_image) 
        
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        cv2.imwrite(folder_path + '/enhanced_image.jpg', enhanced_image)
        print('Enhanced image saved')
    """
    

""" This code is for command line entry. It allows you to add arguments 
    for what you want the code to run on. For instance, if I want to run 
    it on an image called "test1.jpg" with visualizations on, I would 
    type python3 color_id.py test1.jpg True
"""
if __name__ == '__main__':
    import sys
    
    color_id(*sys.argv[1:])
