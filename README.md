# Great American Tweets #

Check out the live map @ [greatamericantweets.com](http://greatamericantweets.com)

This Bokeh application is set up to track and plot tweets onto an interactive map
during the Great American Eclipse.

For a tweet to be plotted, it must contain an image and location and it must have been tweeted from that
location during the eclipse in that location.

To run the app, you'll need conda. Then, follow these commands:

```
$ conda env create -f environment.yml
$ source activate gat
(gat)$ bokeh serve --show gatapp/
