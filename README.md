# Illinois Gambling Analysis
> Using Hierarchical Linear Modeling to infer the relationship between video gambling terminals and casino tax revenue at the municipal level.

## Table of Contents
1. [Purpose](#Purpose)
2. [Background](#Background)
3. [Running the code](#Running-the-code)

# Purpose

In this project I use hierarchical linear models to evaluate the relationship between the number of video gambling terminals within a municipality and the public funds that result from casino revenue while controlling for differences in population between communities. By using hierarchical models, as opposed to the standard Ordinary Least Squares method, I am able to infer the average impact that terminal count has on resulting tax revenue, and the variance that can be expected across communities. 

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

Given the growth that has occurred for video gambling products, increased scrutiny was likely inevitable, but due to the decline in Casino revenue, the differing tax rates between video and casino gambling havee been frequently debated by journalists, voters, and legislators.

### Tax Breakdown

**TLDR;**
> **Casino gambling tax rates increase as revenue increases. The tax rate for video gambling is fixed.**

"*Wagering Tax Effective July 1, 2020, the wagering tax is as follows:*

<u><i>All gambling games, other than table games:</i></u>
- *15% of AGR up to and including \$25 million*
- *22.5\% of AGR in excess of 25 million but not exceeding 50 million*
- *27.5\% of AGR in excess of 50 million but not exceeding 75 million*
- *32.5\% of AGR in excess of 75 million but not exceeding 100 million*
- *37.5\% of AGR in excess of 100 million but not exceeding 150 million*
- *45\% of AGR in excess of 150 million but not exceeding 200 million*
- *50\% of AGR in excess of 200 million

<u><i>All table games:</i></u>
- *15\% of AGR up to and including 25 million*
- *20\% of AGR in excess of 25 million"*

> - [Illinois Gaming Board](https://www.igb.illinois.gov/CasinoFAQ.aspx#:~:text=The\%20Illinois%20Gambling%20Act%20imposes,and\%20a%20tax%20on%20admissions.&text=The\%20admissions%20tax%20was%20increased,person\%20to%20%243%20a%20person.)


![Distribution of tax rates between casinos and video gambling](static/tax_distribution.png)



### Running the code

#### Virtual Environment

To ensure you have all required packages for this notebook, an environment.yml file has been provided [here]().
Follow the set-up instructions [here]() to create and activate the environment.

------

#### Data Collection

The code used for collecting the gambling data can be found [here]()

The code used for collecting census variables can be found [here]()

------

