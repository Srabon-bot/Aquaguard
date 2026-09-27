# Particle swarm optimization based LSTM networks for water level forecasting: A case study on Bangladesh river network
> **Source:** PDF provided by the user.
> **Format:** Markdown transcription/extraction. The text below is preserved from the PDF extraction, page by page. Figure images are included separately and referenced below.
---

## Page 1

```text
                                                                    Results in Engineering 17 (2023) 100951


                                                                   Contents lists available at ScienceDirect


                                                                   Results in Engineering
                                           journal homepage: www.sciencedirect.com/journal/results-in-engineering




Particle swarm optimization based LSTM networks for water level
forecasting: A case study on Bangladesh river network
Jannatul Ferdous Ruma a, Mohammed Sarfaraz Gani Adnan b, c, Ashraf Dewan d,
Rashedur M. Rahman a, *
a
  Department of Electrical & Computer Engineering, North South University, Dhaka, 1229, Bangladesh
b
  Department of Urban and Regional Planning, Chittagong University of Engineering and Technology, Chattogram, 4349, Bangladesh
c
  Environmental Change Institute, School of Geography and the Environment, University of Oxford, Oxford, OX1 3QY, UK
d
  School of Earth and Planetary Sciences, Curtin University, Perth, WA, 6102, Australia




A R T I C L E I N F O                                    A B S T R A C T

Keywords:                                                Floods are one of the most catastrophic natural disasters. Water level forecasting is an essential method of
Long short-term memory                                   avoiding floods and disaster preparedness. In recent years, models for predicting water levels have been
Multivariate time series                                 developed using artificial intelligence techniques like the artificial neural network (ANN). It has been demon­
Neural network
                                                         strated that more advanced and sequenced-based deep learning techniques, like long short-term memory (LSTM)
Particle swarm optimization
Water level forecast
                                                         networks, are superior at forecasting hydrological data. However, historically, most LSTM hyperparameters were
                                                         based on experience, which typically did not produce the best outcomes. The Particle Swarm Optimization (PSO)
                                                         method was utilized to adjust the LSTM hyperparameter to increase the capacity to learn data sequence char­
                                                         acteristics. Utilizing water level observation data from stations along Bangladesh’s Brahmaputra, Ganges, and
                                                         Meghna rivers, the model was utilized to estimate flood dynamics. The Nash Sutcliffe efficiency (NSE) coeffi­
                                                         cient, root mean square error (RMSE), and MAE were used to assess the model’s performance, where PSO-LSTM
                                                         model outperforms the ANN, PSO-ANN, and LSTM models in predicting water levels in all stations. The PSO-
                                                         LSTM model provides improved prediction accuracy and stability and improves water level forecasting accu­
                                                         racy at varying lead times. The findings may aid in sustainable flood risk mitigation in the study region in the
                                                         future.




1. Introduction                                                                               Brahmaputra, and Meghna often create floods across the majority of the
                                                                                              nation because of the substantial monsoon rainfall in the upper catch­
    The most destructive natural catastrophes in the world are floods.                        ments [4–6]. Bangladesh continuously experienced extreme floods in
Floods can have either natural or artificial origins, yet people are                          1954, 1955, 1974, 1987, 1988, 1998 and 2007 [4,7]. In the last decade,
responsible for the destruction in both scenarios. River water level                          several flood incidents occurred in this country in 2017, 2018, and 2019
forecasting is essential to reduce the loss of life and property [1]. Reli­                   [8]. In terms of human suffering and financial loss, floods are one of
able monitoring and cutting-edge river water level detection are                              Bangladesh’s most expensive natural disasters. Annually, 20% of the
essential to protecting the lives and property of those living near the                       country floods, while more than 50% of the country has been drowned
river basin. For this need to be met, highly precise river water level                        by devastating floods in the past [9]. Additional layers of constraints
forecasts are essential [2]. The World Health Organization (WHO) es­                          that affected regions must bear after the floods include loss of human life
timates that more than 2 billion people were affected by floods between                       and farm animals, value escalation, social insecurity, and the expenses of
1998 and 2017. This organization also claims that between 80% and                             infrastructure repair, as well as asset diversion for quick attention and
90% of the natural catastrophes that have occurred in the previous 10                         retrieval. The Ganges, Brahmaputra, and Meghna rivers have highly
years have been caused by floods [3].                                                         seasonal flows that are significantly affected by the monsoon season. As
    More than 300 rivers run across Bangladesh’s territory, which covers                      a result, during the monsoon season, these rivers rise to embankments
an area of around 1,47,000 km2. Major rivers like the Ganges,                                 and often overflow. This is most noticeable in the lower reaches,


    * Corresponding author.
      E-mail addresses: a.dewan@curtin.edu.au (A. Dewan), rashedur.rahman@northsouth.edu (R.M. Rahman).

https://doi.org/10.1016/j.rineng.2023.100951
Received 29 July 2022; Received in revised form 20 January 2023; Accepted 21 January 2023
Available online 10 February 2023
2590-1230/© 2023 The Authors. Published by Elsevier B.V. This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).
```
---

## Page 2

```text
J.F. Ruma et al.                                                                                                              Results in Engineering 17 (2023) 100951




                                                         Fig. 1. Water station locations of different rivers.


                                                                                      especially in Bangladesh, the country with the fewest floodplains [10].
Table 1
                                                                                      Accurate flood forecasting appears to be hampered by uncertainties in
Input and output station list used in the study.
                                                                                      observed and expected water levels, which calls for a forecasting lead
  Network          Input Station                   Output Station                     time of five to ten days to improve flood response and readiness for key
  Name
                                                                                      river basins. Without taking functional utility into account, much effort
  Net_1            SW46.9L                         SW45, SW45.5, SW225, SW49          is being put into developing mechanical hydrological models as well as
  Net_2            SW45.5                          SW294, SW77                        statistical, satellite, and other approaches to enhance lead-time pre­
  Net_3            SW90, SW46.9L                   SW50.6, SW168
  Net_4            SW50.6, SW49                    SW133
                                                                                      dictions [11]. A hydrodynamic model such as MIKE-11, MIKE-21 or
  Net_5            SW90                            SW211.5, SW99                      MIKE-SHE is used worldwide for water level prediction, real-time flood
  Net_6            SW46.9, SW90                    SW277                              forecasting or rainfall-runoff data simulation [12,13]. Hydrodynamic
  Net_7            SW50.6, SW49                    SW273                              models have been used in Bangladesh since the nineteenth century for
  Net_8            SW277                           SW299, SW273
                                                                                      water level forecast [14]. As most of the rivers in Bangladesh are con­
  Net_9            SW273                           SW159, SW202, SW267,
                                                   SW269, SW263                       nected to India, both countries follow a similar flood control method
  SW42             SW45.5, SW88, SW99, SW263,      SW42                               [15]. Analysis and forecasting of seasonal and annual precipitation,
                   SW266, SW159                                                       temperature, river flow and water table are important for local water
                                                                                      resource practices [16].
                                                                                          Estimating future values in a sequence using previous data is known
                                                                                      as time series forecasting. Machine learning approaches are sometimes a

                                                                                  2
```
---

## Page 3

```text
J.F. Ruma et al.                                                                                                          Results in Engineering 17 (2023) 100951




                                      Fig. 2. Structure of river Network (Reproduced from Siddiquee and Hossain [6]).


better choice to solve the constraints of traditional forecasting ap­             which is connected to India and Bangladesh [23]. In this study, Decision
proaches, which are time-consuming and difficult. Different methods               Tree regression performs better than other machine learning techniques
have been applied to forecast water data for last two decades such as             for 10 days of forecasting. In some cases, XGboost algorithm out­
fuzzy technique, Soil and Water Assessment Tool (SWAT) model, ma­                 performs as demonstrated in that research. Siddiquee and Hossain
chine learning models, deep learning techniques and so on [7,17,18].              worked on cascaded channels of Brahmaputra and Ganges water levels
The LSTM approach performs better than the SARIMA and RF methods,                 in Bangladesh which introduced artificial neural network in a faster
according to the findings of the floodwater level forecast in the Red river       method [6]. Later in the Bahadurabad transit, deep learning models
of the North [19]. Water level forecasting in Bangladesh using an arti­           were applied using 15 years of recent data where RNN provided the most
ficial neural network was first introduced by Liong et al. in the early           accurate result in the case study [24]. The LSTM model was built and
twentieth century [18]. The author later studied Dhaka gauge stations             tested to anticipate one-day, two-day, and three-day flood flow in
using a fuzzy model [7]. Biswas et al. worked on the Surma river of               Vietnam stations [25]. Rahman et al. proposed a hybrid method
Bangladesh to predict the water levels of the rivers for water manage­            combining ANN, LR, and frequency ratio where the integrated LR-FR
ment and flood control [20]. Five stations along the Ganges, Brahma­              model gives the highest predictive value in water level data [26]. For
putra and Meghna rivers in Bangladesh’s border region were chosen as              estimating the water levels of 17 harbors in Taiwan, a forecasting model
input nodes for the neural network, with Dhaka on the Buriganga river             based on the long short-term memory (LSTM) recurrent neural network
serving as the output node. The model was developed using river stage             was constructed [27]. Multistep river flow is also forecasted by Hayder
data from 1998 to 2004 and verified using data from 2005 to 2007 [21].            using NARX and LSTM model combination and applied in the Malaysian
Several works have been done using fuzzy logic using ANFIS time series            basin [28]. To estimate flood susceptibility, appropriate feature engi­
forecasting, where a recent work reported on Jamuna river data [22].              neering technique with LSTM is applied in different studies [29,30].
    Recent work has been done on Someshwari-Kangsa Sub-watershed                      Some recent works have been done on stream flow forecasting on

                                                                              3
```
---

## Page 4

```text
J.F. Ruma et al.                                                                                                            Results in Engineering 17 (2023) 100951


          Table 2                                                                   (1) Introduce particle swarm-based neural network models to predict
          Standard Deviation of all the water stations.                                 the water level of different river stations in Bangladesh.
            Water Stations                          Standard Deviation              (2) Apply different lead times and analyze the behavior of PSO based
                                                                                        Neural Network models for different lead time forecasting.
            SW46.9L                                 1.417276
            SW45                                    1.558242                        (3) Find the best model for various river networks by comparing the
            SW45.5                                  1.521192                            prediction performance of different neural network models.
            SW45                                    1.467837
            SW49                                    1.531403                          The rest of the paper is organized as follows. Data set, study area, the
            SW294                                   0.763729
            SW77                                    1.086790
                                                                                  structure of river network is described in Section 2. It also presents
            SW90                                    2.270603                      different data preprocessing techniques and various artificial intelli­
            SW50.6                                  1.51194                       gence techniques that include sequence based modelling like LSTM,
            SW168                                   1.4187                        hybridized models like PSO based LSTM, and ANN based techniques
            SW133                                   1.412321
                                                                                  used in this research. Different performance metrics used to evaluate the
            SW211.5                                 2.63937
            SW99                                    2.4408                        models are also discussed subsequently. Section 3 showcases the results
            SW277                                   0.702169                      and Section 4 presents a discussion on them. Finally, Section 5 concludes
            SW173                                   2.302046                      and gives direction of future research.
            SW299                                   1.113187
            SW273                                   1.113187
            SW88                                    3.064279
                                                                                  2. Materials and methods
            SW263                                   0.785723
            SW266                                   3.521559                      2.1. Study area
            SW159                                   0.919631
                                                                                      Fig. 1 is the visualization of the whole river network of Bangladesh
                                                                                  and the water station locations we have used in our study. We have
                                                                                  considered a total of 24 river station data in our work. Here we tried to
                                                                                  select most of the water station data related to the Ganges, Brahmaputra
                                                                                  and Meghna (GBM) river that are highly responsible for flash floods or
                                                                                  extreme floods in Bangladesh.

                                                                                  2.2. Dataset

                                                                                      We have collected water level data from the Bangladesh Water
                                                                                  Development Board (BWDB) from different gauge stations [36]. All the
                                                                                  water related data are managed by Flood Forecasting & Warning Center
                                                                                  and the organization uses the hydrodynamic model MIKE-11 to calcu­
                                                                                  late the water level. This model has been running in Flood Forecasting
                                                                                  and Warning Center (FFWC) since 1998 [36]. We used data from 1979 to
                                                                                  2009 for time series forecasting of our model. We did not get all of the
                                                                                  stations’ data we used in our study after the year 2009. Later, we added
                                                                                  data till 2014 and used the new augmented data for the prediction of
                                                                                  water level. The major river tidal data has been used in this study. The
                                                                                  major inputs are taken from SW90 and SW46.9L channel data. In our
                                                                                  study, Chittagong Hill tracks water section parts have been discarded
                                                                                  due to the low amount of data availability and also because of not a part
                   Fig. 3. Conventional LSTM model architecture.                  of Ganges, Brahmaputra and Meghna (GBM) river of Bangladesh. We
                                                                                  also covered the water stations of Dhaka and forecasted Buriganga sta­
Orontes Basin in Turkey and rainfall-runoff simulation in China using             tion water level in our research.
particle swarm optimization on neural networks [31,32]. Song et al.                   Table 1 shows the input and output stations that we have taken in our
[31] used only rainfall-runoff data and introduced daily stream flow              study. The stations for Net 1- Net 9 are the same as reported in Ref. [6].
forecasting where different lead day forecasting is missing. Xu et al. [32]       These stations cover the Meghna, Brahmaputra and Ganges River. We
showed maximum 12 h forecasting in daily rainfall-runoff. Yan et al.              additionally introduce a new network of rivers by including the water
[33] also applied the particle swarm based long short term memory on              stations of Dhaka as input to forecast Buriganga station (SW42) water
water quality data to improve the performance over the previously re­             level in our research.
ported work. Another particle swarm based LSTM work was done for
predicting moisture, where results were compared using several evalu­             2.3. Structure of applied river network
ation metrics [34]. For multi-step ahead flood forecasting, various
recurrent neural network models are used for flood forecasting networks               We need to input the SW46.9L and SW90 tidal data which will
[35]. Multiple works are done based on specific river basins and also             sequentially use the outputs to feed the inputs of the other networks. But
with a limited number of river station data. In our current study, we             when we try to predict SW42 water station output, we will take the
have incorporated a total of 24 water stations that constitute a river            output of Net_1 (SW45.5 prediction) and also the other listed water
network. In this network, nine sub-networks are connected where                   stations. These water station data will cover the major rivers’ water
output from a network is fed as input to the other network. To the best of        stations of Bangladesh which will help in flood forecasting in different
our knowledge, the application of hybridized models on such a complex             lead times. Here, Net_1, Net_3 and Net_6 are independent from the other
river network has not been applied yet.                                           networks.
    The contributions of the research are as follows.                                 Fig. 2 is the representation of the major sequencing river network
                                                                                  based on water station channels. Here, Light Blue color is the symbol of
                                                                                  the major input station, light purple is the symbol of output gauges, dark

                                                                              4
```
---

## Page 5

```text
J.F. Ruma et al.                                                                                                                Results in Engineering 17 (2023) 100951




                                          Fig. 4. Applied particle swarm based LSTM algorithm (inspired from Xu et al. [32]).


                                                                                       study is SW46.9L which is placed in Bahadurabad transit. The Brah­
Table 3                                                                                maputra River Basin’s exit was thought to lie near the Bahadurabad
PSO-LSTM model NSE value in 1-day lead time with various time steps, batch
                                                                                       gauging station [38]. Both Hardinge bridge channel (SW90) and Baha­
size and number of cells (Net_1 result is listed here).
                                                                                       durabad (SW46.9L) are the major gauges for the Ganges and Brahma­
  Iterations       Time Steps       Batch Size      Number of Cells      NSE           putra rivers, respectively. The total Bangladesh river system is covered
  10               13               124             124                  0.9524        by the sequential network where some sub networks are created for the
  20               14               124             128                  0.9577        completion of this task.
  40               17               164             128                  0.9644            In NET_1, input is the Bahadurabad transit data (SW46.9L) and four
  60               19               164             224                  0.9698
  80               19               198             224                  0.9779
                                                                                       output gauges are selected. SW45 and SW45.5 are the upstream and
  100              21               221             254                  0.9892        SW49 is the downstream, which is placed at Shirajganj. Here, SW225 is
                                                                                       the affluent river station for Bahadurabad transit. In the presented
                                                                                       sequential network, the output of NET_1 SW45.5 Chilmari station
                                                                                       located on the Brahmaputra-Jamuna River will be the input of NET_2.
Table 4
                                                                                       The output of NET_2 selected SW294 (Kaunia Station) and SW77
Comparison of predicting R values using PSO-LSTM approach with previously
                                                                                       (Kurigram Station). Both of the stations’ data predict the Teesta and
listed work of different sub network.
                                                                                       Dharla river water levels, respectively.
  Network      R value (Siddiquee and Hossain    R value (Applied PSO-LSTM                 When we move forward to NET_3 and NET_6 networks, we take both
               [6])                              approach)
                                                                                       of the major input gauges data SW90 and SW46.9L as the input and for
  Net 1        0.99538                           0.99729                               NET_3, SW50.6 and SW168 as the output. The gauges for the output
  Net 2        0.98789                           0.99006
                                                                                       stations are downstream of the gauges for the input stations, with
  Net 3        0.96357                           0.97114
  Net 4        0.75955                           0.76021                               SW50.6 related to the Brahmaputra-Jamuna river and SW168 related to
  Net 5        0.99333                           0.99410                               the Faridpur station. NET_4, NET_7 and NET_8 are dependent on the
  Net 6        0.93113                           0.94237                               intermediate input station SW50.6 which we got from NET_3 output.
  Net 7        0.95357                           0.95519                               SW50.6 is considered as an intermediate gauge because it is related to
  Net 8        0.91356                           0.91455
  Net 9        0.91248                           0.91398
                                                                                       Brahmaputra river. In this case, NET_4 takes only one input and predicts
  SW42         –                                 0.99371                               SW133, which is Naogaon Station and is related to the Jamuna River.
                                                                                       Another network, NET_7 covers the Sylhet area and takes both SW50.6
                                                                                       and SW49 as input and SW173A (Sheola Station) is the output. NET_6
grey is the symbol of intermediate gauges and light green is shown for                 output covers the Chandpur station, which is related to Surma-Meghna
the created network name. The major input gauges we selected here are                  river.
SW90 and SW46.9L. SW90 is the channel of Hardinge Bridge and is                            Later in this research, we added SW277 and SW50.6 as input of
situated in the Ganges River. This station gives the incoming water level              NET_8 and then the output of this network selected SW299 (Tongi) and
data of the Ganges river [37]. Another major input channel used in this                SW273 (Bhairab Bazar). This SW273 gauge output data is inserted as the


                                                                                   5
```
---

## Page 6

```text
J.F. Ruma et al.                                                                                                                     Results in Engineering 17 (2023) 100951




Fig. 5. NSE result with (a) time step values and batch size, (b) Number of cells and batch size and (c) number of cells and time cells, first row (1 day lead), second row
(7 days lead) and third row (15 days lead) (Net_1 results).


input of NET_9 and gives SW159 (Habiganj), SW202 (Moulvi Bazar),                        cover the major water station of the city of Bangladesh. To get the
SW267 (Sylhet), SW269 (Dirai_on Kalni) and SW263 (Madhanagar). All                      output, we considered one previous intermediate gauge output
of the input and output of the NET_9 cover the Sylhet district of                       (SW45.5) and the other stations SW88, SW99, SW263, SW266, and
Bangladesh for water level forecasting. Another independent network                     SW159 as input. The inputs of this network are related to the Meghna
NET_5 is only dependent on the main input gauge SW90 and predict the                    and Ganges basin which helps to predict the Buriganga river water level.
SW99 (Gorai Railway Bridge) and SW211.5 (Chapai Nawabganj) in the
output.                                                                                 2.4. Data analysis
    The sequential networks are planned to execute from NET_1 to
NET_9 one by one because some of the inputs are dependent to the other                     The standard deviation of the water stations data that we evaluated
NET outputs. The sequence of net building. e.g., from NET_1 to NET_9                    was determined. Table 2 depicts all the results.
tracked the flow of the river via the branches. In this river networking
system, NET_1, NET_3, NET_6 and NET_5 are independent to the other
                                                                                        2.5. Data preprocessing
network’s outputs.
    We have additionally incorporated Dhaka station in current research
                                                                                           In the first step of preprocessing the data, we applied the data
to predict SW42 channel of Dhaka_Mill Barrack (Buriganga River) to
                                                                                        imputation technique to fill in the missing values. For the data impu

                                                                                    6
```
---

## Page 7

```text
J.F. Ruma et al.                                                                                                                 Results in Engineering 17 (2023) 100951


Table 5                                                                               2.6.1. PSO algorithm
Average performance comparison of different water stations on 15 days lead                Many global optimization techniques built on a metaphor inspired by
time.                                                                                 nature have been developed over the years. Kennedy and Eberhart [39]
  Network          Model        NSE        RMSE        MAE          MAPE              discuss the idea of using a particle swarm technique to optimize
  Net 1            ANN          0.9036     1.1994      0.9671       0.0707
                                                                                      nonlinear functions based on observations of bird migration and eating
                   PSO-ANN      0.9216     1.1812      0.9432       0.0682            behavior. According to the technique, people are viewed as particles in a
                   LSTM         0.8753     1.5914      1.4148       0.0883            multidimensional search space, with each particle standing in for a
                   PSO-LSTM     0.9475     1.1143      0.9531       0.0595            potential answer to the optimization problem. Location, velocity, and
  Net 2            ANN          0.7136     0.8701      0.7356       0.02987           fitness value are used as the three variables to characterize the particle
                   PSO-ANN      0.7411     0.8633      0.7305       0.02899           attributes. The fitness value is determined by the fitness function. Based
                   LSTM         0.7122     0.8635      0.739        0.02997           on the ideal global fitness value, the particle independently alters its
                   PSO-LSTM     0.7687     0.8567      0.7291       0.02781
                                                                                      direction of motion and its distance, eventually choosing the optimum
  Net 3            ANN          0.7804     1.036       0.9691       0.1604            [40].
                   PSO-ANN      0.7921     1.005       0.8847       0.1575
                                                                                          The PSO system is configured with random variables and updated
                   LSTM         0.7811     1.104       0.9572       0.1589
                   PSO-LSTM     0.84021    0.9135      0.7016       0.1488            after each cycle in order to identify the best choice. Each potential so­
                                                                                      lution, denoted as a particle, is represented by a point in the multidi­
  Net 4            ANN          0.7743     1.301       0.40         0.315
                   PSO-ANN      0.7896     1.117       0.394        0.294
                                                                                      mensional solution space. As they search for the ideal solution, the
                   LSTM         0.7782     1.275       0.413        0.302             particles move at a set speed into the solution region. According to its
                   PSO-LSTM     0.7948     1.0051      0.28         0.259             experiences and those of its neighbors, each particle changes its location
  Net 5            ANN          0.8013     1.73        1.46         1.42              and velocity. Correctly, each particle follows the optimum solution path.
                   PSO-ANN      0.8354     1.61        1.38         1.29              Personal best representative, or pbest, is the name of this solution. The
                   LSTM         0.8299     1.47        1.39         1.33              system also keeps track of the global best path for all swarms, known as
                   PSO-LSTM     0.8506     1.22        1.17         1.28
                                                                                      gbest. At each repeat, the primary principle of PSO is to alter the velocity
  Net 6            ANN          0.8301     1.79        0.921        0.98              of each swarm towards the pbest and gbest places [41]. During
                   PSO-ANN      0.8398     1.36        0.835        0.87              balancing exploration and exploitation, the PSO system combines a local
                   LSTM         0.8219     1.73        0.798        0.87
                                                                                      search method with global techniques.
                   PSO-LSTM     0.8653     1.29        0.702        0.83
                                                                                          Assume k particles in an M-dimensional space form a group A = a1,
  Net 7            ANN          0.7251     1.88        0.724        0.1788
                                                                                      a2, ak, with ai = [ai1, ai2, aiM]. The following are the present properties of
                   PSO-ANN      0.7593     1.78        0.717        0.1525
                   LSTM         0.7313     1.91        0.728        0.1713            the i-th particle:
                   PSO-LSTM     0.7873     1.69        0.691        0.1269                 (                      )T
                                                                                      Ai = ati1 , ati2 , …., atiM                                               (2)
  Net 8            ANN          0.7327     1.95        0.736        0.1698
                   PSO-ANN      0.7391     1.76        0.731        0.1407                (                       )T
                   LSTM         0.7309     1.91        0.749        0.1533            Vi = vti1 , vti2 , …., vtiM                                                   (3)
                   PSO-LSTM     0.7598     1.70        0.727        0.1335
                                                                                          (                       )T
  Net 9            ANN          0.7376     1.246       0.708        0.0296            Pi = pti1 , pti2 , …., ptiM                                                   (4)
                   PSO-ANN      0.7578     1.29        0.738        0.0289
                   LSTM         0.7387     1.361       0.719        0.0301                (                       )T
                   PSO-LSTM     0.7692     1.102       0.726        0.0282            Pg = ptg1 , ptg2 , …., ptgM                                                   (5)
  SW42             ANN          0.8981     0.991       0.8534       0.119
                                                                                           In equations (2) and (3), ati and vti are the current location and the
                   PSO-ANN      0.9024     0.903       0.8567       0.118
                   LSTM         0.8891     0.921       0.932        0.130             current velocity, where Pti and Ptg are the optimum location in the par­
                   PSO-LSTM     0.9287     0.847       0.842        0.113             ticle’s and the overall particle swarm’s history. The velocity and the
                                                                                      position changes per iteration using following conditions (7) and (8).
                                                                                                                              (          )
tation technique, we used the k-nearest neighbor approach. After that,                vt+1
                                                                                                           (         )
                                                                                            = wvti + C1 Rt1 pti − ati + C2 Rt2 ptg − ati                      (7)
we used the following equation, Eq. (1), to conduct min-max normali­
                                                                                       i

zation on the input features since different stations had varying absolute
                                                                                      at+1 = ati + vt+1                                                             (8)
values of water level. The dataset is first separated into the train and test          i            i

sets, and then normalization is used to avoid losing information from the
                                                                                      Here, vt+1  and at+1 shows the how velocity update after each iteration
training set.                                                                                 i         i
                                                                                      and position after the iteration respectively. C1 and C2 represents the
Normalised data =
                       q − Qmin
                                                                            (1)       constants and R1 and R2 are arbitrary integers between (0, 1).
                      Qmax − Qmin                                                         In the recent works, PSO is used for optimal sizing of the parameter.
   We used the initial 80% of data for training and the remaining 20%                 It produces better result than other optimization method in forecasting
data to validate our applied model. In our case study, we introduced                  application [42]. This algorithm is also applied for optimization of
multivariate multi-step time series forecasting with particle swarm                   artificial neural network model parameters for prediction [43].
optimization.
                                                                                      2.6.2. LSTM algorithm
2.6. Hybridization of long short term memory (LSTM)                                       Hochreiter and Schmidhuber [44] introduced long short term
                                                                                      memory which includes forget gate, memory cell, output gate. A con­
    In this section, we have discussed the algorithms, i.e., Particle Swarm           ventional LSTM model is presented in Fig. 3. A long short term memory
Optimization (PSO), Long Short Term Memory (LSTM), Traditional Back                   neural network is a RNN that allows previously entered data to be kept
Propagation Neural Network and their hybrid models. Additionally, we                  inside the network without impacting the output. Zhang et al. [45]
also addressed the hyperparameters, model construction, and perfor­                   shows in their study that the gradient vanishing is an exponential ex­
mance measures used to assess the models.                                             plosion that hinders typical RNNs from learning long-term relationships
                                                                                      in data. The LSTM model’s structure enables it to manage short data
                                                                                      dependencies and also massive ones.


                                                                                  7
```
---

## Page 8

```text
J.F. Ruma et al.                                                                                                             Results in Engineering 17 (2023) 100951




Fig. 6. Water level prediction models (a) NSE, (b) RMSE, (c) MAE and (d) MAPE values of 15 days forecasting using all the applied models (Net_1 is shown here).


   We applied stacked LSTM to train our model. LSTM model is                       2.6.5. Model configuration and parameterization
preferred for prediction and forecasting of multi class classification                 We used python 3.9 for the programming language and implemented
studies [46].                                                                      PSO using python, Tensorflow for model training and testing. Initially,
                                                                                   preprocess the data using python libraries that can be used by LSTM
2.6.3. Artificial neural network (ANN)                                             networks and forecast 1-day, 5-day, 7-day, 11-day and 15-day ahead
    ANN is commonly used as a tool for identifying nonlinear systems               water level using different time steps as a sliding window.
and is typically employed for learning complicated tasks such as iden­                 For this experiment, we used batch size [64, 512], time step [4,30]
tification, decision making, or forecasting [47]. An input layer, hidden           and number of cells [64, 512] for the particle swarm to find the opti­
(containing neurons), and output layers make up a typical feedforward              mization for the best combination in river basin data. We also defined
neural network. According to recent studies, utilizing ANN is one of the           learning rate 0.0001, activation function ‘tanh’ to build the model. The
most important ways for simulating hydrological processes [48].                    number of epoch we set to 30 and set the early stopping to avoid
                                                                                   overfitting the model. When we trained the model, we also set the
2.6.4. PSO-LSTM algorithm                                                          patience to 5.
    The initial settings of the parameters in the LSTM neural network
have a significant impact on the network’s efficiency. The PSO tech­               2.6.6. Performance evaluation method
nique was used to improve two important LSTM network parameters in                     We applied different methods to evaluate our model. Statistical error
this study. The number of buried layer neurons and the learning rate are           metrics such as the root mean square error (RMSE), Nash-Sutcliffe effi­
the two factors. A conventional LSTM network prediction model was                  ciency (NSE), Mean Absolute Error (MAE) and Mean Absolute Percent­
done as a priority while developing the suggested model. Following that,           age Error (MAPE) are used to assess the performance of several models
PSO was used to improve numerous LSTM model hyperparameters. The                   in this study.
PSO algorithm’s best outcomes were found, then inserted as a parameter                 In the equations, n represents the total number of test values.
to the LSTM network, and the LSTM model was retrained. We applied                      The root mean square error, or RMSE, is a commonly used statistic
PSO to optimize the parameters of LSTM.                                            for assessing predicting accuracy. Equation (9) is the representation of
    Fig. 4 is the illustration of PSO-LSTM algorithm where for a specific          RMSE.
iteration, model will find out the best parameter based on Nash–Sutcliffe                    √̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
model efficiency coefficient (NSE).                                                            ∑      (actual − pred)2
                                                                                                 n
                                                                                   RMSE =                                                                (9)
                                                                                               i=1
                                                                                                                     n



                                                                               8
```
---

## Page 9

```text
J.F. Ruma et al.                                                                                                                             Results in Engineering 17 (2023) 100951



                                                                                                  1∑ n
                                                                                                        |actual − pred|
                                                                                       MAPE =                           × 100%                                                    (12)
                                                                                                  n i=1      actual

                                                                                           R value is measured for water level prediction by Siddiquee and
                                                                                       Hossain in Ref. [6] which is also referred as Pearson’s correlation co­
                                                                                       efficient and shows the equation in equation (13). The correlation co­
                                                                                       efficient is a measurement of the degree of linear connection between
                                                                                       predicted and actual data [49]. R value varies from − 1 to +1. R values
                                                                                       with +1 indicating a positive connection, − 1 indicating a negative
                                                                                       correlation, and 0 indicating no relation.
                                                                                                 ∑n
                                                                                                      i=1 (actuali − actual)(predi − pred)
                                                                                       R = √̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
                                                                                              ∑n                                                                                    (13)
                                                                                                                                         2 ∑n                                     2
                                                                                                 i=1 (actuali − actual)                         i=1 (predi − pred)


                                                                                           We use the corrected Akaike information criterion (AICc) introduced
                                                                                       by Suguira [50] to compare the applied sequential models and also the
                                                                                       hybridized model performances in our study with different lead time
                                                                                       forecasting. equation (14) is the representation of AICC where k is the
                                                                                       total number of parameters of model. This AICC value is also applied by
                                                                                       Ren et al. [51] for real-time water level prediction in their study.
                                                                                                      (                        )
                                                                                                    1 ∑n                             2k (k + 1)
                                                                                       AICC = n. ln                          2
                                                                                                              (pred − actual) + 2k +                        (14)
                                                                                                    n     i=1                         n− k− 1


                                                                                       3. Results

                                                                                           We evaluated the parameters using PSO for all the stations we have
                                                                                       selected, as shown in Table 1. Here, in Table 3, we can observe the NSE
                                                                                       value improvement when iterations of PSO models have been increased.
                                                                                       When the iteration value is small, which is 10, batch size value is 124
                                                                                       and number of cells 124 and NSE value we achieved 0.9524 for the input
                                                                                       of SW46.9L. Here, we forecasted only 1 day lead values for find out in
                                                                                       which iteration step we can get the highest NSE values. The NSE value of
                                                                                       the initial iteration value is much lower compared to the other values of
                                                                                       NSE. When we have increased the iterations to 20, 40, 60, the NSE value
                                                                                       is much higher. Initially, NSE value was 0.9577, but when we iterate the
                                                                                       model 40 times, with time step value 17, batch size 164 and number of
                                                                                       cells 128 NSE value reaches 0.9644 which is very much higher
                                                                                       compared to the initial iteration.
                                                                                           We also observed that if we increase the iteration number and batch
                                                                                       size together in this algorithm, NSE value finally reaches to 0.9892. This
                                                                                       value is highest for our input station SW46.9 where the output stations
Fig. 7. The predicted water levels (a) 1 day, (b) 7 day and (c) 15 day lead time
                                                                                       are SW45, SW45.5, SW225 and SW49. For our data, PSO provides higher
forecast of four water stations using PSO-LSTM model (NET_1 outputs shown in
the graph).
                                                                                       NSE value in 100 iterations and time step 21 and LSTM number of cell
                                                                                       assigned to 254.
                                                                                           Later in our experiment, we take the iteration step 100 which pro­
    The Nash–Sutcliffe model efficiency coefficient is abbreviated as
                                                                                       vides the highest NSE compared to the lower number of iteration steps
NSE. The performance of a model is determined using this statistical
                                                                                       (reported in Table 3). In this step, we used all of our gauge station data
criterion. Equation (10) is the representation of NSE.
                                                                                       which is enlisted in Table 1. We reported the NSE values with various
           ∑n
              i=1 (actual − pred)
                                 2                                                     lead time in days in Table 3. When the lead time increases the perfor­
NSE = 1 − ∑ n                                                    (10)                  mance of the model slowly decreases. The highest NSE value 0.9892 is
               (actual − actual)2
              i=1
                                                                                       reported in 1-day lead time for NET 1. We have listed 5, 7, 11 and 15
                                                                                       days lead time NSE values with different hyperparameter tuned values.
   The mean absolute error is denoted as MAE. MAE enables us to                        When lead time increased in 5 days, time step is increased and NSE value
determine how effectively the models are able to forecast and by what                  we get here 0.9801 which is quite good in terms of NSE value. Because
margin these values differ from the real value.                                        NSE value larger than 0.75 considered as good model and in between
         ∑
         n                                                                             value of 0.75 to 0.5 is considered as average model performance [52,
             |actual − pred|
                                                                                       53]. Finally, when time step is higher among all the previous forecasted
MAE = i=1                                                                  (11)        output, 24, NSE value is 0.9577 in 15 day lead forecasting in Net_1.
                    n
                                                                                           We determined R values for the networks which are listed in Table 4
   The above equation (11) shows the calculation method of MAE.
                                                                                       for prediction. We can see that R value is notably improved throughout
   Another evaluation metrics we used in our study is MAPE which
                                                                                       the river networks. When we noted the value from Net 1, we observed
denotes mean absolute percentage error. The following equation (12) is
                                                                                       that R value improved around 0.00191. The listed previous work using
the representation of MAPE equation.
                                                                                       ANN NET_1 value reported 0.99538 where in our approached method,
                                                                                       we achieved 0.99729. In Net 2, we also improved the R value using


                                                                                   9
```
---

## Page 10

```text
J.F. Ruma et al.                                                                                                              Results in Engineering 17 (2023) 100951




Fig. 8. Water level model prediction comparison using average AICc/1000 values in different river subnetworks in 1-day, 5-day, 7-day, 11-day and 15-day lead time
of subnetworks (a) NET 1, (b) NET 2, (c) NET 3, (d) NET 4, (e) NET 5, (f) NET 6, (g) NET 7, (h) NET 8, (i) NET 9, and (j) SW42.



introduced model and get around 0.99006. In Net_3, we improved the R                row of Fig. 5, we can see that when time step and batch size is higher
value around 0.00757 that is higher than the previous ones. Almost                  together the NSE values reaches around 0.988. But when batch size is
every networks R value is enhanced by PSO-LSTM model. SW42 gauge                    lower and number of cells are higher, the NSE values low compared to
station R value we received 0.99371 which is quite good and close to                the other values.
positive 1. The highest improvement we achieved in terms of R values in                 When we observed 7 days lead time, the highest NSE value falls down
NET 6 which is 0.01124.                                                             to 0.975. But with a higher number of time step, the number of cell value
    Fig. 5 is the representation of the combination of different time step,         gives good number of NSE value. In 15 days lead time prediction, NSE
number of cells and NSE values with various lead times. From the first              value falls down around 0.03 compared to the 1 day ahead forecast. But


                                                                               10
```
---

## Page 11

```text
J.F. Ruma et al.                                                                                                       Results in Engineering 17 (2023) 100951




                                                                Fig. 8. (continued).


when we forecasted 15 days ahead forecast for all the number of cells          LSTM than the LSTM model.
output did not differ much in terms of accuracy.                                   Fig. 6 is the representation of ANN, PSO_ANN, LSTM and PSO-LSTM
    In the experiment, every water station produced NSE data with              for different lead time forecasting scenarios. The NSE value of ANN and
different time steps, batch sizes and number of LSTM layer cells.              LSTM is quite closer compared to the PSO applied models. We recorded
    From all the experiments we used 100 iterations for hyperparameter         the highest NSE value when we applied PSO-LSTM algorithm. Initially,
tuning using PSO, and achieved the highest accuracy when we predicted          LSTM and ANN give similar results, but later, when lead time increased,
1 day ahead water level. But when we increased the lead time, we also          PSO optimized models perform way better than benchmark models like
observed that we had to increase the time step as the sliding window to        ANN and LSTM neural networks.
forecast the future water level data. For Net 1 we reported the highest            When we recorded RMSE value, initially in 1 day lead time, error
forecasted value of NSE, which is 0.957 in 15 days ahead of prediction.        value was around 0.9787 in PSO-LSTM. But, when we applied 15 days
    From all the gathered experiment data, we observed that with a high        lead time, error value increased but less than 1.1146. But the RMSE
number of cell, time step and batch size, we can get better NSE values         value of LSTM was initially greater than 1.32 and later, when lead time
which helps to predict the future data much better than the lower              increased, ANN and LSTM error values increased more and reached
number of lag data or time step data. The highest number of the cell we        around 1.1996 and 1.5914. In this case, PSO-ANN provides better per­
used 398 here by particle swarm optimization in SW42 water station             formance compared to ANN and LSTM.
data forecasting.                                                                  Fig. 6(c) shows the MAE values where we observed that PSO-LSTM
    We compared the PSO-LSTM results for all the sub networks we used          outperforms compared to other models. Though the MAE value is
in the study with three other neural network models. The results of the        greater than 0.90 for our network Net_1, the results are comparatively
comparison with models are listed in Table 5. In terms of NSE value,           better than the other three experimented models in this study. PSO-ANN
PSO-LSTM provides higher accuracy compared to all other experiments            model value also performs better than the LSTM and ANN models.
we conducted. The average NSE value is 0.9475 in 15 days lead fore­                Fig. 6(d) shows the MAPE values we observed throughout a multiple
casting whereas LSTM provides the lowest amongst the other ones which          number of lead times using our experimented models. The highest MAPE
is 0.8753. The PSO optimized ANN gives a much more accurate result             value obtained using PSO-LSTM in a 15-day lead time is 0.0573, whereas
than the PSO-LSTM that is 0.9216 but not more than the PSO optimized           it was lower in a 1-day ahead forecast, at 0.0215. MAPE metric results of
LSTM model. We also recorded the RMSE, MAE and MAPE values for all             PSO-ANN and ANN are slightly overlapping throughout the 15-day
the networks. RMSE value for Net_1 is around 0.0423 lower in PSO-              forecasting period. But the LSTM result is quite higher compared to


                                                                          11
```
---

## Page 12

```text
J.F. Ruma et al.                                                                                                                      Results in Engineering 17 (2023) 100951


Table 6                                                                                      best, we compared the applied models using AICc values. We have tal­
Comparative analysis of water level prediction work, forecasting and ap­                     lied the values of various lead periods, with 1-day lead times having
proaches in different regions.                                                               higher values than 15-day lead times.
  Study            Research           Dataset         Method          Findings                   For the simplicity of explanation, we compared the results using the
                   Purpose                                                                   absolute value, and based on the AICc criterion value from Fig. 8, the
  Ghorbani         River stage and    Dulhunty        Cascade         0.862 NSE              PSO-LSTM model is a better option.
   et al.          river flow         River and       correlation     value in
   [54]            prediction in      Herbert         neural          Dulhunty               4. Discussion
                   Australia          River in        network and     River and
                                      Australia       the random      0.885 Herbert
                                                      forest model    River                      From the overall performance of the applied model, LSTM model
  Ren et al.       Real-time          River water     RWLP model      RMSE                   gives poorer prediction results compared to other hybridized models and
    [51]           water level        level data in   using LSTM as   0.008790 in 6          ANN model. But ANN model gives a much better AICc criterion value but
                   prediction of      China           hidden layer    h lead time            is slightly lower than the PSO optimized ANN model results. But in all
                   cascaded                                           using LSTM
                   channels                                           model
                                                                                             the subnetworks, hybridized LSTM model outperforms and is proved as
  Pan et al.       Water Level        Yangtze         CNN-GRU         5-day ahead            the best fit after optimizing the parameter based on NSE values. Though
    [55]           Prediction         River in        model           forecast and           15-day lead time performance is not as good as 1-day lead time results
                                      China 30                        0.9747 NSE             according to other evaluation measure metrics but still our optimized
                                      years data                      values
                                                                                             model can predict the better values.
  Palash           A Model for        GBM             ReqSim QQ +     Flood forecasts
    et al.         Forecasting        streamflow      ObsR + ForeR    up to 10 days              From Table 6, we can see the comparative results of the water level
    [11]           Streamflow         or WL data      model           for the GBM            prediction works and methodologies. It is clearly shown that, compared
                   and Water          of                              basins. 0.95 R2        to previously reported work on cascaded water level prediction in
                   Levels on the      Bangladesh                      value 0.95 and         Bangladesh, we built a model that performs way better in terms of R
                   Ganges,                                            0.92 for
                   Brahmaputra,                                       Ganges and
                                                                                             values. And also, it provides 15 day forecasting ahead, which was not
                   and Meghna                                         Brahmaputra            reported in the previous work. We have also evaluated the hybridized
                   Rivers                                             respectively.          model using 2010 to 2014 data that also provided better results after
  Noor et al.      Water Level        Dhaka and       Spatio-         7 days ahead           optimization. Different works have been listed for short term water level
   [56]            Forecast of        Sylhet gauge    temporal        forecast of
                                                                                             forecasting but a long term forecasting like 15 day ahead using hy­
                   Bangladesh         station river   LSTM model      Dhaka and
                   River              data                            Sylhet stations        bridized model in Bangladesh river network was not applied yet.
  Siddiquee        River water        Major rivers    Artificial      R value                    According to previous works, no other experiments till now can
    and            level prediction   of              Neural          0.99538,               perform better than the applied hybridized model in the large and
    Hossain                           Bangladesh      network         0.98789,               complex river network in Bangladesh. The optimized model is also
    [6]                               except          model           0.96357,
                                      Chittagong                      0.75955,
                                                                                             evaluated using the AICc metric, which also ensures the effectiveness of
                                      Hill tracks                     0.99333,               the applied architecture. The models we applied in our study listed
                                      related river                   0.93113,               sequentially in terms of NSE values for all the sub networks is LSTM - >
                                      data                            0.95357,               ANN- > PSO-ANN - > PSO-LSTM where LSTM gives inferior perfor­
                                                                      0.91356,
                                                                                             mance and the PSO optimized LSTM gives the best performance.
                                                                      0.91248 for all
                                                                      the nine river
                                                                      network                5. Conclusion
                                                                      respectively.
  Our Study        Water level        24 river        PSO             1–15 days                  The current research uses the PSO method to improve the LSTM
                   prediction case    stations data   optimized       water level
                   study of           of              hybridized      prediction. R
                                                                                             network hyperparameters. The hyperparameter sizes are adjusted based
                   Bangladesh         Bangladesh      LSTM model      value 0.99729,         on the NSE value, so the model can handle different situations. To get
                   river network      with            and             0.99006,               better results from the PSO algorithm, different hyperparameters are
                                      cascaded        performance     0.97114,               chosen. The batch size is over 256, the timestep is kept around 24, and
                                      network         evaluated       0.76021,
                                                                                             the lead time is varied with the number of cells in the hidden layer. The
                                                      using AICc      0.99410,
                                                      metric with     0.94237,               lead time and river basin data qualities both have an impact on the
                                                      ANN, PSO-       0.95519,               hyperparameter selection. The built-in neural network can effectively
                                                      ANN and         0.91455,               learn the input data and prevent overfitting during training. We have
                                                      LSTM            0.91398 for all        compared the results of subnetwork predictions using the R-value with
                                                                      the
                                                                      subnetworks
                                                                                             previous studies performed using artificial neural networks. Nearly all of
                                                                      respectively           the tested subnetworks show greater R-values when the suggested model
                                                                      and 0.99371            is used. This NSE-optimized PSO-LSTM algorithm performed better
                                                                      for SW42 river         while covering Bangladesh’s river network. This is useful for 15 days
                                                                      network.
                                                                                             ahead flood forecasting.
                                                                                                 The PSO-LSTM model provides higher performance values such as
the other three models we used in this case study.                                           NSE, RMSE. We have applied only water level data to find out an optimal
   We have applied 2010–2014 years data for predicting the water                             model which can provide better results compared to conventional neural
levels. Fig. 7(a) depicts the 1-day lead time forecasting values with                        network models. We investigated time series analysis utilizing the PSO
actual data and the PSO-LSTM optimized prediction, demonstrating that                        deep learning approach, which hasn’t been done before in this part of
the SW45 output is much closer than the other station outputs. When we                       Bangladesh. Further study can be done on other station data of
increased the lead time to 7 days (Fig. 7(b)), the difference between                        Bangladesh to find better results. This study can be enhanced by using
actual and predicted values was higher than the 1-day lead time. If we                       weather, and rainfall data to predict flood more accurately.
increase the lead time to 15 days (Fig. 7(c)), the error between fore­
casted and actual water level data becomes high.                                             Contribution
   In order to determine which model fits the applied river network the
                                                                                                Jannatul     Ferdous    Ruma:     Conceptualization,       Methodology,

                                                                                        12
```
---

## Page 13

```text
J.F. Ruma et al.                                                                                                                                 Results in Engineering 17 (2023) 100951


Software, Formal analysis, Validation, Writing - Original Draft, Writing -                      [16] A.R.M.T. Islam, M.R. Karim, M.A.H. Mondol, Appraising trends and forecasting of
                                                                                                     hydroclimatic variables in the north and northeast regions of Bangladesh, Theor.
Review & Editing, Visualization; Mohammed Sarfaraz Gani Adnan:
                                                                                                     Appl. Climatol. 143 (2021) 33–50, https://doi.org/10.1007/S00704-020-03411-0/
Methodology, Formal analysis, Software; Ashraf Dewan: Data curation,                                 TABLES/6.
Visualization; Rashedur M. Rahman.: Investigation, Resources, Fund­                             [17] Raihan F, Beaumont LJ, Maina J, Saiful Islam A, Harrison SP. Simulating
ing acquisition, Writing - Original Draft, Writing - Review & Editing.                               streamflow in the Upper Halda Basin of southeastern Bangladesh using SWAT
                                                                                                     model. Https://DoiOrg/101080/0262666720191682149 2019;65:138–51.
                                                                                                     https://doi.org/10.1080/02626667.2019.1682149.
                                                                                                [18] S.-Y. Liong, W.-H. Lim, G.N. Paudyal, river stage forecasting in Bangladesh: neural
Declaration of competing interest                                                                    network approach, J. Comput. Civ. Eng. 14 (2000) 1–8, https://doi.org/10.1061/
                                                                                                     (ASCE)0887-3801(2000)14:1(1).
                                                                                                [19] V. Atashi, H.T. Gorji, S.M. Shahabi, R. Kardan, Y.H. Lim, Water level forecasting
    The authors declare that they have no known competing financial                                  using deep learning time-series analysis: a case study of Red river of the North,
interests or personal relationships that could have appeared to influence                            Water 14 (2022) 1971.
the work reported in this paper.                                                                [20] R.K. Biswas, A. Jayawardena, K. Takeuchi, Prediction of Water Levels in the Surma
                                                                                                     River of Bangladesh by Artificial Neural Network, 2009, https://doi.org/
                                                                                                     10.13140/2.1.4718.5921.
Data availability                                                                               [21] A.S. Islam, A.A.S. Islam, Improving flood forecasting in Bangladesh using an
                                                                                                     artificial neural network, J. Hydroinf. 12 (2010) 351–364, https://doi.org/
                                                                                                     10.2166/HYDRO.2009.085.
    Data will be made available on request.
                                                                                                [22] S.C. Sarkar, A. Bashar, M.S. Mahmud, R.I. Rasel, Application of soft-computing for
                                                                                                     time series water-level prediction in Jamuna River, Int. J. Syst. Innov. 6 (2021)
Acknowledgement                                                                                      13–21, https://doi.org/10.6977/IJOSI.202112_6(6).0003.
                                                                                                [23] M. Hamidul Haque, M. Sadia, M. Mustaq, M. Hamidul Haque, M. Sadia, M. Mustaq,
                                                                                                     Development of flood forecasting system for someshwari-Kangsa sub-watershed of
   This work was supported by the Ministry of Post, Telecommunication                                Bangladesh-India using different machine learning techniques, EGUGA (2021),
and Information Technology, Bangladesh through ICT Innovation Fund                                   https://doi.org/10.5194/EGUSPHERE-EGU21-15294. EGU21-15294.
                                                                                                [24] Rabbi II, M. Galib, MdA. Hasan, Water Level Prediction of Bahadurabad Transit of
(2020–21) round 3: Grant Number 12.                                                                  Brahmaputra-Jamuna Using Deep Learning Models, 2022.
                                                                                                [25] X.H. Le, H.V. Ho, G. Lee, S. Jung, Application of Long Short-Term Memory (LSTM)
                                                                                                     neural network for flood forecasting, Water Switz. 11 (2019), https://doi.org/
Appendix A. Supplementary data
                                                                                                     10.3390/W11071387.
                                                                                                [26] M. Rahman, C. Ningsheng, M.M. Islam, A. Dewan, J. Iqbal, R.M.A. Washakh, et al.,
   Supplementary data to this article can be found online at https://doi.                            Flood susceptibility assessment in Bangladesh using machine learning and multi-
org/10.1016/j.rineng.2023.100951.                                                                    criteria decision analysis, Earth Syst. Environ. 3 (2019 33 2019) 585–601, https://
                                                                                                     doi.org/10.1007/S41748-019-00123-Y.
                                                                                                [27] C.H. Yang, C.H. Wu, C.M. Hsieh, Long short-term memory recurrent neural
References                                                                                           network for tidal level forecasting, IEEE Access 8 (2020) 159389–159401, https://
                                                                                                     doi.org/10.1109/ACCESS.2020.3017089.
                                                                                                [28] G. Hayder, M.I. Solihin, M.R.N. Najwa, Multi-step-ahead prediction of river flow
 [1] M. Imran, P. Sheikh Abdul Khader, M. Rafiq, K. Singh Rawat, Forecasting water
                                                                                                     using NARX neural networks and deep learning LSTM, H2Open J. 5 (2022) 42–59,
     level of Glacial fed perennial river using a genetically optimized hybrid Machine
                                                                                                     https://doi.org/10.2166/H2OJ.2022.134/989976/H2OJ2022134.PDF.
     learning model, Mater. Today Proc. 46 (2021) 11113–11119, https://doi.org/
                                                                                                [29] R. Bentivoglio, E. Isufi, S.N. Jonkman, R. Taormina, Deep learning methods for
     10.1016/j.matpr.2021.02.256.
                                                                                                     flood mapping: a review of existing applications and future research directions,
 [2] Y. Li, H. Shi, H. Liu, A hybrid model for river water level forecasting: cases of
                                                                                                     Hydrol. Earth Syst. Sci. Discuss. (2022) 1–50.
     Xiangjiang River and Yuanjiang River, China, J. Hydrol. 587 (2020), 124934,
                                                                                                [30] Z. Fang, Y. Wang, L. Peng, H. Hong, Predicting flood susceptibility using LSTM
     https://doi.org/10.1016/j.jhydrol.2020.124934.
                                                                                                     neural networks, J. Hydrol. 594 (2021), 125734, https://doi.org/10.1016/j.
 [3] Floods, n.d. https://www.who.int/health-topics/floods. (Accessed 11 December
                                                                                                     jhydrol.2020.125734.
     2022). accessed
                                                                                                [31] Y. Song, H. Wang, H.C. Kilinc, Daily streamflow forecasting based on the hybrid
 [4] M. Ali, T. Mahjabin, T. Hosoda, IMPACT OF CLIMATE CHANGE ON FLOODS OF
                                                                                                     particle swarm optimization and long short-term memory model in the Orontes
     BANGLADESH AND INTRODUCING FLOOD INTENSITY INDEX TO
                                                                                                     Basin, Water 14 (2022), https://doi.org/10.3390/W14030490, 490 2022;14:490.
     CHARACTERIZE THE FLOODING SCENARIO, 2012.
                                                                                                [32] Y. Xu, C. Hu, Q. Wu, S. Jian, Z. Li, Y. Chen, et al., Research on particle swarm
 [5] Paudyal GN. Forecasting and warning of water-related disasters in a complex
                                                                                                     optimization in LSTM neural networks for rainfall-runoff simulation, J. Hydrol.
     hydraulic setting—the case of Bangladesh. Https://DoiOrg/101080/
                                                                                                     608 (2022), 127553, https://doi.org/10.1016/J.JHYDROL.2022.127553.
     02626660209493018 2009;47:S5–18. https://doi.org/10.1080/0262666020
                                                                                                [33] J. Yan, X. Chen, Y. Yu, X. Zhang, Application of a parallel particle swarm
     9493018.
                                                                                                     optimization-long short term memory model to improve water quality data, Water
 [6] M. Siddiquee, M. Hossain, Development of a sequential Artificial Neural Network
                                                                                                     11 (2019), https://doi.org/10.3390/W11071317, 1317 2019;11:1317.
     for predicting river water levels based on Brahmaputra and Ganges water levels,
                                                                                                [34] F. Chen, X. Gao, X. Xia, J. Xu, Using LSTM and PSO techniques for predicting
     Neural Comput. Appl. 26 (2015) 1–12, https://doi.org/10.1007/s00521-015-1871-
                                                                                                     moisture content of poplar fibers by Impulse-cyclone Drying, PLoS One 17 (2022),
     6.
                                                                                                     e0266186, https://doi.org/10.1371/JOURNAL.PONE.0266186.
 [7] S.-Y. Liong, W.H. Lim, T. Kojiri, T. Hori, Advance flood forecasting for flood
                                                                                                [35] F.J. Chang, P.A. Chen, Y.R. Lu, E. Huang, K.Y. Chang, Real-time multi-step-ahead
     stricken Bangladesh with a fuzzy reasoning method, Hydrol. Process. 14 (2000),
                                                                                                     water level forecasting by recurrent neural networks for urban flood control,
     https://doi.org/10.1002/(SICI)1099-1085(20000228)14:33.0.CO;2-0.
                                                                                                     J. Hydrol. 517 (2014) 836–846, https://doi.org/10.1016/J.
 [8] K. Uddin, M.A. Matin, Potential flood hazard zonation and flood shelter suitability
                                                                                                     JHYDROL.2014.06.013.
     mapping for disaster risk mitigation in Bangladesh using geospatial technology,
                                                                                                [36] BWDB, Processing and Flood Forecasting Circle, 2022. Dhaka, Bangladesh.
     Prog. Disaster Sci. 11 (2021), 100185, https://doi.org/10.1016/j.
                                                                                                [37] S.B. Murshed, J.J. Kaluarachchi, Scarcity of fresh water resources in the Ganges
     pdisas.2021.100185.
                                                                                                     Delta of Bangladesh, Water Secur. 4–5 (2018) 8–18, https://doi.org/10.1016/J.
 [9] M.R. Chowdhury, An assessment of flood forecasting in Bangladesh: the experience
                                                                                                     WASEC.2018.11.002.
     of the 1998 flood, Nat. Hazards 22 (2000 222 2000) 139–163, https://doi.org/
                                                                                                [38] K. Mohammed, A.K.M. Saiful Islam, G.M. Tarekul Islam, L. Alfieri, S.K. Bala, M.
     10.1023/A:1008151023157.
                                                                                                     J. Uddin Khan, Impact of high-end climate change on floods and low flows of the
[10] R. Chowdhury, N. Ward, Hydro-meteorological variability in the greater
                                                                                                     Brahmaputra River, J. Hydrol. Eng. 22 (2017), 4017041.
     Ganges–Brahmaputra–Meghna basins, Int. J. Climatol. 24 (2004) 1495–1508,
                                                                                                [39] R. Eberhart, J. Kennedy, Particle swarm optimization, Proc. IEEE Int. Conf. Neural
     https://doi.org/10.1002/JOC.1076.
                                                                                                     Netw. 4 (1995) 1942–1948. Citeseer.
[11] W. Palash, Y. Jiang, A.S. Akanda, D. Small, A. Nozari, S. Islam, A streamflow and
                                                                                                [40] R.K. Huda, H. Banka, New efficient initialization and updating mechanisms in PSO
     water level forecasting model for the Ganges, Brahmaputra and Meghna rivers with
                                                                                                     for feature selection and classification, Neural Comput. Appl. 32 (2020)
     requisite simplicity, J. Hydrometeorol. 19 (2017), https://doi.org/10.1175/JHM-
                                                                                                     3283–3294, https://doi.org/10.1007/S00521-019-04395-3/TABLES/6.
     D-16-0202.1.
                                                                                                [41] A. Medina, G. Toscano Pulido, J. Ramírez-Torres, A Comparative Study of
[12] A.H. Kamel, Application of a hydrodynamic MIKE 11 model for the Euphrates river
                                                                                                     Neighborhood Topologies for Particle Swarm Optimizers, 2009.
     in Iraq, Slovak. J. Civ. Eng. 2 (2008) 1–7.
                                                                                                [42] S.I. Abba, B.G. Najashi, A. Rotimi, B. Musa, N. Yimen, S.J. Kawu, et al., Emerging
[13] R.K. Panda, N. Pramanik, B. Bala, Simulation of river stage using artificial neural
                                                                                                     Harris Hawks Optimization based load demand forecasting and optimal sizing of
     network and MIKE 11 hydrodynamic model, Comput. Geosci. 36 (2010) 735–745.
                                                                                                     stand-alone hybrid renewable energy systems– A case study of Kano and Abuja,
[14] J.C. Refsgaard, K. Havnø, H.C. Ammentorp, A. Verwey, Application of hydrological
                                                                                                     Nigeria, Res. Eng. 12 (2021), 100260, https://doi.org/10.1016/j.
     models for flood forecasting and flood control in India and Bangladesh, Adv. Water
                                                                                                     rineng.2021.100260.
     Resour. 11 (1988) 101–105, https://doi.org/10.1016/0309-1708(88)90043-7.
                                                                                                [43] A. Kerboua, F.B. Hacene, M.F.A. Goosen, L.F. Ribeiro, Development of technical
[15] M.M. Rahman, N.K. Goel, D.S. Arya, Development of the Jamuneswari flood
                                                                                                     economic analysis for optimal sizing of a hybrid power system: a case study of an
     forecasting system: case study in Bangladesh, J. Hydrol. Eng. 17 (2011)
     1123–1140, https://doi.org/10.1061/(ASCE)HE.1943-5584.0000565.


                                                                                           13
```
---

## Page 14

```text
J.F. Ruma et al.                                                                                                                                    Results in Engineering 17 (2023) 100951

     industrial site in Tlemcen Algeria, Res. Eng. 16 (2022), 100675, https://doi.org/           [50] N. Sugiura, Further analysts of the data by akaike’ s information criterion and the
     10.1016/j.rineng.2022.100675.                                                                    finite corrections, Commun. Stat. Theor. Methods 7 (1978) 13–26, https://doi.org/
[44] S. Hochreiter, J. Schmidhuber, Long short-term memory, Neural Comput. 9 (1997)                   10.1080/03610927808827599.
     1735–1780, https://doi.org/10.1162/neco.1997.9.8.1735.                                      [51] T. Ren, X. Liu, J. Niu, X. Lei, Z. Zhang, Real-time water level prediction of cascaded
[45] J. Zhang, X. Wang, C. Zhao, W. Bai, J. Shen, Y. Li, et al., Application of cost-                 channels based on multilayer perception and recurrent neural network, J. Hydrol.
     sensitive LSTM in water level prediction for nuclear reactor pressurizer, Nucl. Eng.             585 (2020), 124783.
     Technol. 52 (2020) 1429–1435, https://doi.org/10.1016/J.NET.2019.12.025.                    [52] W. Feng, G. Huang, Y. Li, J. Xu, G. Wang, J. Zhang, et al., A statistical hydrological
[46] A.K. Abdella Ahmed, A.M. Ibraheem, M.K. Abd-Ellah, Forecasting of municipal                      model for Yangtze river watershed based on stepwise cluster analysis, Front. Earth
     solid waste multi-classification by using time-series deep learning depending on                 Sci. 9 (2021), https://doi.org/10.3389/feart.2021.742331.
     the living standard, Res. Eng. 16 (2022), 100655, https://doi.org/10.1016/j.                [53] D.N. Moriasi, J.G. Arnold, M.W. Van Liew, R.L. Bingner, R.D. Harmel, T.L. Veith,
     rineng.2022.100655.                                                                              Model evaluation guidelines for systematic quantification of accuracy in watershed
[47] A. Wibowo, S.H. Arbain, Time Series Methods for Water Level Forecasting of                       simulations, Trans. ASABE (Am. Soc. Agric. Biol. Eng.) 50 (2007) 885–900.
     Dungun River in Terengganu Malaysia, 2012.                                                  [54] M.A. Ghorbani, R.C. Deo, S. Kim, M. Hasanpour Kashani, V. Karimi, M. Izadkhah,
[48] S.K. Ahmad, F. Hossain, A generic data-driven technique for forecasting of                       Development and evaluation of the cascade correlation neural network and the
     reservoir inflow: application for hydropower maximization, Environ. Model.                       random forest models for river stage and river flow prediction in Australia, Soft
     Software 119 (2019) 147–165, https://doi.org/10.1016/J.ENVSOFT.2019.06.008.                      Comput. 24 (2020) 12079–12090, https://doi.org/10.1007/s00500-019-04648-2.
[49] D.N. Moriasi, M.W. Gitau, N. Pai, P. Daggupati, Hydrologic and water quality                [55] M. Pan, H. Zhou, J. Cao, Y. Liu, J. Hao, S. Li, et al., Water level prediction model
     models: performance measures and evaluation criteria, Trans. ASABE (Am. Soc.                     based on GRU and CNN, IEEE Access 8 (2020) 60090–60100.
     Agric. Biol. Eng.) 58 (2015) 1763–1785.                                                     [56] F. Noor, S. Haq, M. Rakib, T. Ahmed, Z. Jamal, Z.S. Siam, et al., Water level
                                                                                                      forecasting using spatiotemporal attention-based long short-term memory
                                                                                                      network, Water 14 (2022) 612, https://doi.org/10.3390/w14040612.




                                                                                            14
```
---

## Extracted Figure Images

The following images are the figures extracted directly from the PDF. Their captions and surrounding text remain in the page-by-page transcription above.

### Figure 1 — Water station locations of different rivers

![Figure 1 — Water station locations of different rivers](article_assets/figure-003.png)

### Figure 2 — Structure of river Network

![Figure 2 — Structure of river Network](article_assets/figure-004.png)

### Figure 3 — Conventional LSTM model architecture

![Figure 3 — Conventional LSTM model architecture](article_assets/figure-005.png)

### Figure 4 — Applied particle swarm based LSTM algorithm

![Figure 4 — Applied particle swarm based LSTM algorithm](article_assets/figure-006.png)

### Figure 5 — NSE result with time step, batch size and number of cells

![Figure 5 — NSE result with time step, batch size and number of cells](article_assets/figure-007.png)

### Figure 6 — Water level prediction models

![Figure 6 — Water level prediction models](article_assets/figure-008.png)

### Figure 7 — Predicted water levels at different lead times

![Figure 7 — Predicted water levels at different lead times](article_assets/figure-009.png)

### Figure 8 — Water level model prediction comparison

![Figure 8 — Water level model prediction comparison](article_assets/figure-010.png)

### Figure 8 (continued)

![Figure 8 (continued)](article_assets/figure-011.png)

---

## End of PDF transcription

