# Illinois Gambling Analysis
> Using Hierarchical Linear Modeling to infer the relationship between video gambling terminals and casino tax revenue at the municipal level.

## Table of Contents
1. [Purpose](#Purpose)
2. [Background](#Background)
3. [Running the code](#Running-the-code)

# Purpose

In this notebook I use hierarchical linear models to evaluate the relationship between the number of video gambling terminals within a municipality and the public funds that result from casino revenue while controlling for differences in population between communities. By using hierarchical models, as opposed to the standard Ordinary Least Squares method, I am able to infer the average impact that terminal count has on resulting tax revenue, and the variance that can be expected across communities. 

## Background

Video gambling was legalized by the state of Illinois in 2009, with the first machines activated in September of 2012. Since then the number of towns that have installed video gambling machines has increased every year.
> **Note:** All video gambling activities were suspended from April 2020-June 2020 to mitigate transmission of COVID19. While data for 2020 has been reported by the [Illinois Gaming Board](https://www.igb.illinois.gov/) these data require further clarification by the Illinois Gaming Board before they can be confidently analyzed. Because of this, 2020 data  is largely excluded from this analysis and excluded entirely from the models developed in this notebook. 

![timeline](static/video_gambling_growth_timeline.png)

**Prior to the legalization of video gambling**, if an Illinois residents had wanted to gamble their only option was to travel to one of the few municipalities home to a casino.

![casino locations](static/casino_locations.png)

**However**, since activation of video gambling in 2012, access to gambling facilities have become widely distributed throughout the state.

![terminal locations 2019](static/terminal_locations_2019.png)

During this same time, **Illinois has also seen a near consistent decline in casino revenue.**

![casino revenue decline](static/casino_decline.png)

### Running the code

#### Virtual Environment

To ensure you have all required packages for this notebook, an environment.yml file has been provided [here]().
Follow the set-up instructions [here]() to create and activate the environment.

#### SQL or Pandas?

*TL;DR* Either is fine. The notebook can be run with or without the database.

>This notebook uses data that has been scraped from the [illinois gaming board website](https://www.igb.illinois.gov/) and inserted into a postgresql database. The code in the cell below checks if the database has been created. If so, the notebook will run using postgresql. If the database has not been creeated or if the database is empty, the data for this project have been provided as csv files. In this second case, the notebook will handle all data manipulations in pandas. 
You may choose to run the scraping and database creation code or not. Each code cell begins with an if check to determine if the database is created and then activate the sql or pandas code accordingly.

------

#### Data Collection

The code used for collecting the gambling data can be found [here]()

The code used for collecting census variables can be found [here]()

------

