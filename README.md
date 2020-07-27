# Google Places Extractor

The Google Maps Places [API](https://cloud.google.com/maps-platform/places/) opens up access to Google Maps' directory of over 150 million points of interest. However, the API is configured to make it difficult to extract bulk location data for any one place. The Nearby Places search parameter allows users to input a coordinate and a radius and retrieve up to 25 points of interest within that radius. By putting together a recursive algorithm that checks if the 25 place threshold has been exceeded, one is able to progressively drill down and extract all of the data within a given radius of a point, obtaining place data for whole neighborhoods or even cities. 
    
`placeextractor` is a Python script for extracting place data within a given radius of a point. 

Note that by virtue of the progressive focused radial search, results for the entire radius will be incomplete; complete results will only be returned for a bounding sqaure that fits entirely within the radius. i.e., if you wish to capture all of the places within a X-mile equal sided bounding box with your point at the center, the required radius is equal to (x*sqrt(2))/2 - a  
5 mile bounding square contained within a circle with a radius of 3.535 

![GIF of Recursion](/example.gif)

## Install and Use

Clone the directory, navigate to the directory of the .py file via command line, and run the placeextractor.py file - passing it your Google Places API Key, the POI type, location as a single string, and search radius in the same command.<br>
E.g.: `> python placeextractor.py "[API_KEY]" "food" "33.834312,-118.315724" "5"`
<br>
<br>
Returned fields available include:  
* Place Name
* Unique Google ID
* Operating Status
* Latitude
* Longitude
* Rating
* Number of Ratings
* Price Level
* POI Type Tags
