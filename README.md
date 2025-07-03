# Computational Single and Budded Yeast Area Measurement


## Abstract


## Introduction


## Methods


### Required Input



### Image Pre-processing

The input image is first processed with the Canny edge detection algorithm [1]. This particular algorithm is selected over other algorithms to reduce background noise's interference with the results.

The specific Canny edge detection implementation in use here is the one within the CV2 module [2]. The `cv2.Canny` function therein takes two parameters in addition to the image being analyzed: a lower threshold and a higher threshold. These values alter the sensitivity of the algorithm and may need to be altered depending on the thickness of cell walls. The lower threshold controls the low end of what could possibly be considered an edge while the higher threshold controls the bounds where something is certainly an edge. It is important to note when editing this parameter that if the thresholds are set to be too accepting, edges of small buds may appear where they should not because of unfiltered interference. On the other hand, if the thresholds are too unforgiving, the algorithm may miss sides of yeast walls leaving incomplete and incorrect area measurements.

The function outputs a black and white image, with black being background and white being the detected outlines of cells. For our purposes, we invert the image such that the background is white and the cell outlines are black, as shown in Figure 1. In Figure 2, you can see the outlines overlayed on the original yeast image as well as how other noise was correctly filtered out.

![Isolated Outlines.](demonstration/preprocessing/cleaned_test.png)




![Outlines overlaid on source experiment.](demonstration/preprocessing/results_of_test.png)



### Filling Outlines

All of the outlines discovered by the Canny edge detection algorithm need to be filled in to find the area of the yeast. In order to do this, the image is searched row by row for the first black pixel it encounters.

After a black pixel is found, its coordinate is added to a Queue. Until the Queue is empty, an item is taken from it and added to a list of found edge pixels. Any of the 8 pixels surrounding that coordinate that are also black are added to the same Queue. 

Once the Queue is empty and all of the coordinates contained within it have been added to the list of found edge pixels, the area of the yeast is ready to be filled based on that list. A simple flood fill is insufficient due to the gaps in some of the outlines, so a more sophisticated methodology is needed. In order to meet our needs, a dynamic programming approach is used wherein a two dimentional array of integers is constructed such that a bit mask can be used to determine if an edge exists anywhere in a given direction from any position in the array. 


First, a 2D array with enough width and height to accomodate the currently found outline is made. The outline coordinates are adjusted to this new coordinate plane and the integers in their positions are set to equal 0x111111111, or, in integer terms, 255 + 256. This means that they count as being surrounded on all sides since every bit mask will find that direction to be True (Table 1), while also being differentiable from a non-outline pixel that is completely surrounded due to the additional 256. 


Table 1. 

| Direction    | Bit Mask    | Integer Value |
| :----------: | :---------: | :-----------: |
| Top          | 0x000000001 | 1             |
| Bottom       | 0x000000010 | 2             |
| Left         | 0x000000100 | 4             |
| Right        | 0x000001000 | 8             |
| Top Left     | 0x000010000 | 16            |
| Top Right    | 0x000100000 | 32            |
| Bottom Left  | 0x001000000 | 64            |
| Bottom Right | 0x010000000 | 128           |



After all of the original pixels are marked, each direction is scanned starting from the most extreme pixels of that direction and moving towards the least extreme. For example, when the Top direction is being scanned, the array will be read from top to bottom while checking if the integer stored directly above the current one in the array evaluates to True when the bit mask for Top is applied, 0x000000001. If it is True, then the current position is also surrounded on the top and its integer value is set to reflect that. The first row is not run through because there is no row above the first row. This means that the "Top" status is accumulated as the already set outline is encountered, and to complete the operation each direction needs to run through the entire 2D array one time. This would ultimately run with linear time complexity.


With the 2D bit mask array in place, each position in that array is evaluated how much it is surrounded by the yeast outline. There are 8 sides in total, which includes diagonals, so if a pixel is surrounded by the outline on more than 5 sides it is in the center of a yeast. If a pixel was only surrounded on 5 sides, it has likelyformed a 90 degree angle, which is more likely a divot outside a yeast representing the divide between two actively budding yeast. That space should not be filled, so our lower bounds for surounded sides must be 5. Unfortunately, there are some edge cases where a line moves diagonally and the top right pixel is not filled while the corresponding bottom left pixel is also unfilled, leaving a gap in the yeast area. This can be remedied by running over the area one more time for good measure with all of the found values being the edges. Pixels that are still surrounded on exactly 5 sides and no more after a second run of this code represent divoted areas. 


All of these inner coordinates are added to the array of edge coordinates to create a full array whose length is the pixel area of the potential yeast. 


However, we are still not done with this area. Next we need to search around the found area in order to see if there are any other black pixels nearby that are close enough to count as buds. If there are any black pixels within `MAX_BUDDING_DISTANCE` of any pixel of the area we found, that black pixel is the next area to fill. This generates a list where every item in the list is a different area and every area is a list of coordinates.


These areas are set to a new, non-black color and the process is started again by searching for another black pixel until there are none left.



### Categorizing Areas

As areas are accumulated by filling in outlines, each one is categorized as either a single yeast, budded yeasts, or a cluster. Single yeasts and budded yeasts are of interest while "clusters" are disregarded. The color of each kind of yeast can be customized when they are filled in on the original image. 

First, the issue of multiple yeast blending together because of the edge detection must be addressed. For example, the cells in the upper left of Figure 1 are in a cluster of three, but two of them appear attached to one another. Simply counting the distinct number of seperated areas to determine if the cells are budded would not be accurate here since it would count the three cells as two, with one of them being misleadingly large. This is where the divot areas discussed earlier come into play. These areas represent divots in the outline of the cell. Two divots are likely the divide between a cell and its bud, while one divot is likely a fluke. More than two divots or a particularly large divot likely means a malformed yeast which should be categorized as a cluster or ignored. 

The next step in categorizing a found set of areas is by filtering out any areas in the list that are too small, meaning they have a smaller pixel count than `IGNORE_ALL_SIZE` or one of the included areas was within `MAX_BUDDING_DISTANCE` of the edge of the image, meaning the reading could be incomplete or there could be another yeast outside of the frame of view that would be within budding distance.

Once all areas have been as acceptable yeast to include, the array of areas can be treated as final. If there is only one area left in the array, it should be added to the single yeast list. If there are exactly two areas in the array, it is catagorized as a budded yeast and put in that list. Otherwise it is counted as a cluster and discarded since the parent and child of the budding cannot be determined accurately.






### Output

The program will create a directory wherever you are in your file system with the same name as the file you are analyzing. Inside this directory it will generate two csv files and three image files. 

There will be one csv file containing information for budded yeasts, while another will contain information for single yeasts. These files will incude all found yeasts with ID numbers, areas, and coordinates. 

The three images will include an image of the Canny outlines, an image of the finished test with areas color coded based on their classification overlaid on the original image, and a copy of the color coded image where every cell is labeled with its ID correlating to the IDs listed in the two csv files. The order of the IDs is not reflective of anything meaningful. Some numbers may be skipped.



## Evaluation

For this algorithm to be used in any journal or paper, the output images showing the yeast and how they were categorized should be included either as figures or as supplemental materials. For reproducability, any parameters such as `MAX_BUDDING_DISTANCE` or  `IGNORE_ALL_SIZE` that were changed from the defaults should also be included.



## Works Cited

1. https://www.researchgate.net/publication/224377985_A_Computational_Approach_To_Edge_Detection

2. https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
