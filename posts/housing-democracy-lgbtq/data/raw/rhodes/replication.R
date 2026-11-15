#laboratories of democratic renewal
#replication code
#this R script contains all of the code needed to replicate
#the tables and figures in "Laboratories of Democratic Renewal"

########################################################
#load necessary packages
library(logr)
library(tidyverse)
library(DataExplorer)
library(MCMCpack)
library(FactoMineR)
library(factoextra)
library(BayesFM)
library(stargazer)
library(hrbrthemes)
library(QCApro)
library(cna)
library(causalHyperGraph)
library(frscore)
library(haven)
library(texreg)
library(ggeffects)
library(jtools)

########################################################
#set working directory to replication directory (this is mine; reset to yours)
setwd("~/Dropbox/Voting Rights in the States Research/CNA Article Draft/R & R/Replication Materials")

#########################################

#create Electoral Democracy Score

#load all datasets and combine into single file

COVI2000 <- read.csv("COVI2000revised.csv")
COVI2004 <- read.csv("COVI2004revised.csv")
COVI2008 <- read.csv("COVI2008revised.csv")
COVI2012 <- read.csv("COVI2012revised.csv")
COVI2016 <- read.csv("COVI2016revised.csv")
COVI2020 <- read.csv("COVI2020revised.csv")
COVI2022 <- read.csv("COVI2022revised.csv")

#rbind COVI datasets
dataset <- rbind(COVI2000, COVI2004)
dataset <- rbind(dataset, COVI2008)
dataset <- rbind(dataset, COVI2012)
dataset <- rbind(dataset, COVI2016)
dataset <- rbind(dataset, COVI2020)
dataset <- rbind(dataset, COVI2022)

#add EPI measures
epi <- read.csv("epi-all-years-revised.csv")

dataset <- left_join(dataset, epi, join_by(State, Year))

#add gerrymandering measures
conggerry <- read.csv("planscore_congress_gerrymandering.csv")
statehousegerry <- read.csv("planscore_statehouse_gerrymandering.csv")
statesenategerry <- read.csv("planscore_statesenate_gerrymandering.csv")

dataset <- left_join(dataset, conggerry, join_by(State, Year))
dataset <- left_join(dataset, statehousegerry, join_by(State, Year))
dataset <- left_join(dataset, statesenategerry, join_by(State, Year))

#add ineligible felons data
felons <- read.csv("mcdonald-ineligible-felons.csv")

dataset <- left_join(dataset, felons, join_by(State, Year))

#load variables list
variables <- read.csv("variables.csv")

#Impute NAs (acknowledgments to Grumbach 2023)
for(i in variables$variable){
  cat(i, "\n")
  
  dataset$temp <- as.numeric(dataset[,i])
  dataset$temp[is.na(dataset$temp)] <- mean(dataset$temp, na.rm=T)
  dataset[,i] <- dataset$temp
  
}
dataset$temp <- NULL

#Bayesian Factor Analysis (acknowledgments to Grumbach 2023)
mcmcmodel <- MCMCfactanal(~ RegDeadlines + NoSameDayReg +	NoPollPlaceReg + NoFelonsReg + NoFelonsRegAfterIncar + NOonlineregistration +	NoDriveAllowed + NoPR +	AbsenteeExcuseReq +	NoAbsenteeInPerson + nostateholiday +	NoEarlyVote +	noallmailvoting +	mustcastballotinprecinct + NoAutomaticregDMV + NoPermanentAbsentee + nonstrictID + nonstrictPhoto +	strictID + strictPhoto + PollHrsAvg +	somepollreductionspost2012 + website_pollingplace +	website_reg_status + website_precinct_ballot + website_absentee_status + website_provisional_status +	reg_rej +	prov_partic +	prov_rej_all + abs_rej_all_ballots + abs_nonret +	uocava_rej + uocava_nonret + nonvoter_reg_onyear_pct + eavs_completeness + post_election_audit + nonvoter_illness_onyear_pct + wait +	pct_reg_of_vep_vrs + EG_cong_abs + declination2_cong_abs + mean_median_cong_abs +	symmetry_cong_abs +	EG_statehouse_abs +	declination2_statehouse_abs +	mean_median_statehouse_abs +	symmetry_statehouse_abs +	EG_statesenate_abs +	declination2_statesenate_abs + mean_median_statesenate_abs + symmetry_statesenate_abs +	Ineligible_Felons_Percent,
                          data = dataset,
                          factors=1,
                          lambda.constraints = list(
                            EG_cong_abs=list(1,"-"),
                            website_precinct_ballot=list(1,"+"),
                            uocava_rej=list(1,"-"),
                            Ineligible_Felons_Percent=list(1,"-"),
                            pct_reg_of_vep_vrs=list(1,"+"),
                            NoSameDayReg=list(1,"-"),
                            somepollreductionspost2012=list(1,"-"),
                            website_pollingplace=list(1,"+")
                          ), 
                          burnin = 1000, mcmc = 1000,
                          thin=1,
                          store.scores=T, verbose=0
)

mcmc <- data.frame(summary(mcmcmodel)$statistics)
mcmc_scores <- mcmc[grepl("phi.", row.names(mcmc)), ]

mcmc_summary <- data.frame(summary(mcmcmodel)[[1]])
mcmc_summary$variable <- rownames(mcmc_summary)
mcmc_summary <- mcmc_summary[grepl("phi_",mcmc_summary$variable)==F,]
mcmc_summary$parameter[grepl("Lambda",mcmc_summary$variable)] <- "discrimination"
mcmc_summary$parameter[grepl("Lambda",mcmc_summary$variable)==F] <- "difficulty"
mcmc_summary$variable <- gsub("Lambda","",mcmc_summary$variable)
mcmc_summary$variable <- gsub("Psi","",mcmc_summary$variable)
mcmc_summary$variable <- gsub("_1","",mcmc_summary$variable)
mcmc_summary$cilow <- mcmc_summary$Mean - 1.96*mcmc_summary$Naive.SE
mcmc_summary$cihigh <- mcmc_summary$Mean + 1.96*mcmc_summary$Naive.SE

mcmc_summary$variable_full <- factor(mcmc_summary$variable, 
                                     levels=unique(mcmc_summary$variable[order(mcmc_summary$Mean)]))

mcmc_summary <- left_join(mcmc_summary, variables[,c("variable","description")])

mcmc_summary$description_full <- factor(mcmc_summary$description, 
                                        levels=unique(mcmc_summary$description[order(mcmc_summary$Mean)]))

dataset$democracy_mcmc <- mcmc_scores$Mean
dataset$democracy_mcmc_sd <- mcmc_scores$SD
dataset$democracy_mcmc_se <- mcmc_scores$Naive.SE

#checking discrimination parameters (acknowledgments to Grumbach 2023): Supplemental Information #2

pdf("discrimination_loadings2.pdf", h=7, w=7)
ggplot(mcmc_summary[mcmc_summary$parameter=="discrimination",], 
       aes(x=description_full, y=Mean)) +
  geom_point()  +
  geom_errorbar(aes(ymin=(Mean - 1.96*SD), 
                    ymax=(Mean + 1.96*SD)), width=0) +
  xlab("Variable") +
  ylab("Discrimination Parameter") +
  coord_flip() +
  geom_hline(yintercept=0, linetype=2) +
  theme_bw()
dev.off()

#write MCMC loadings
write.csv(mcmc_summary, "mcmc_paper_loadings.csv")

#democracy MCMC dataset
write.csv(dataset, "democracy_dataset.csv")
#########################################################
#Validation of EDS: Figures 1 and 2, and Supplemental Information 3, 4, and 5

#Comparison of EDS and SDI (Figure 1 and Supplemental Information 3)

#read in EDS and SDI 
rhodes <- read.csv("democracy_dataset.csv")
grumbach <- read.csv("SDI_2.0.csv")

#limit datasets to same year numbers
rhodes_small <- rhodes %>%
  filter(Year==2000|Year==2004|Year==2008|Year==2012|Year==2016|Year==2020|Year==2022) %>%
  dplyr::select(Year, State, democracy_mcmc)

grumbach_small <- grumbach %>%
  filter(Year==2000|Year==2004|Year==2008|Year==2012|Year==2016|Year==2020|Year==2022) %>%
  dplyr::select(Year, State, democracy_mcmc_grumbach)

#combine EDS and SDI datasets
combined <- left_join(rhodes_small, grumbach_small, join_by(State, Year))

#examine correlation (across years)
cor(combined$democracy_mcmc, combined$democracy_mcmc_grumbach)

#correlation and plot of EDS and SDI for each year
#2000 (Supplemental Info 3)
rg_2000 <- combined %>%
  filter(Year==2000)

cor(rg_2000$democracy_mcmc, rg_2000$democracy_mcmc_grumbach)

rgplot2000<- ggplot(rg_2000, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2000") +
  ylim(-2.5,2.5) + 
  xlim(-2.5,2.5)

ggsave("rgplot2000.png", rgplot2000, width = 4, height = 3, bg = "white")

#2004 (Supplemental Info 3)
rg_2004 <- combined %>%
  filter(Year==2004)

cor(rg_2004$democracy_mcmc, rg_2004$democracy_mcmc_grumbach)

rgplot2004 <- ggplot(rg_2004, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2004") +
  ylim(-2.5,2.5) + 
  xlim(-2.5,2.5)

ggsave("rgplot2004.png", rgplot2004, width = 4, height = 3, bg = "white")

#2008 (Supplemental Info 3)
rg_2008 <- combined %>%
  filter(Year==2008)

cor(rg_2008$democracy_mcmc, rg_2008$democracy_mcmc_grumbach)

rgplot2008 <- ggplot(rg_2008, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2008") +
  ylim(-2.5,2.5) + 
  xlim(-2.5,2.5)

ggsave("rgplot2008.png", rgplot2008, width = 4, height = 3, bg = "white")

#2012 (Supplemental Info 3)
rg_2012 <- combined %>%
  filter(Year==2012)

cor(rg_2012$democracy_mcmc, rg_2012$democracy_mcmc_grumbach)

rgplot2012 <- ggplot(rg_2012, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2012") +
  ylim(-2.5,2.5) + 
  xlim(-2.5,2.5)

ggsave("rgplot2012.png", rgplot2012, width = 4, height = 3, bg = "white")

#2016 (Supplemental Info 3)
rg_2016 <- combined %>%
  filter(Year==2016)

cor(rg_2016$democracy_mcmc, rg_2016$democracy_mcmc_grumbach)

rgplot2016 <- ggplot(rg_2016, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2016") +
  ylim(-4,4) + 
  xlim(-4,4)

ggsave("rgplot2016.png", rgplot2016, width = 4, height = 3, bg = "white")

#2020 (Figure 1)
rg_2020 <- combined %>%
  filter(Year==2020)

cor(rg_2020$democracy_mcmc, rg_2020$democracy_mcmc_grumbach)

rgplot2020 <- ggplot(rg_2020, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2020") +
  ylim(-4,4) + 
  xlim(-4,4)

ggsave("rgplot2020.png", rgplot2020, width = 4, height = 3, bg = "white")


#2022 (Supplemental Info 3)
rg_2022 <- combined %>%
  filter(Year==2022)

cor(rg_2022$democracy_mcmc, rg_2022$democracy_mcmc_grumbach)

rgplot2022 <- ggplot(rg_2022, aes(x=democracy_mcmc, y=democracy_mcmc_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("State Democracy Index") +
  ggtitle("2022") +
  ylim(-4,4) + 
  xlim(-4,4)

ggsave("rgplot2022.png", rgplot2022, width = 4, height = 3, bg = "white")

################################################################
#Comparison of EDS and COVI (Supplemental Information 4)

#add COVI dataset
covi <- read.csv("covi.csv")

#create small COVI dataset and merge with combined dataset to facilitate validation
covi_small <- covi %>%
  filter(Year==2000|Year==2004|Year==2008|Year==2012|Year==2016|Year==2020|Year==2022) %>%
  dplyr::select(State,Year,FinalCOVI)

#combine covi dataset with rhodes and grumbach datasets
combined <- left_join(combined, covi_small, join_by(State, Year))

#correlation between EDS and COVI across all years
cor(combined$democracy_mcmc, combined$FinalCOVI)

#correlation and plot of EDS and COVI for each year
#2000
rc_2000 <- combined %>%
  filter(Year==2000)

cor(rc_2000$democracy_mcmc, rc_2000$FinalCOVI)

rcplot2000 <- ggplot(rc_2000, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2000") 

ggsave("rcplot2000.png", rcplot2000, width = 6, height = 4, bg = "white")

#2004

rc_2004 <- combined %>%
  filter(Year==2004)

cor(rc_2004$democracy_mcmc, rc_2004$FinalCOVI)

rcplot2004 <- ggplot(rc_2004, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2004") 

ggsave("rcplot2004.png", rcplot2004, width = 6, height = 4, bg = "white")

#2008
rc_2008 <- combined %>%
  filter(Year==2008)

cor(rc_2008$democracy_mcmc, rc_2008$FinalCOVI)

rcplot2008 <- ggplot(rc_2008, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2008") 

ggsave("rcplot2008.png", rcplot2008, width = 6, height = 4, bg = "white")

#2012
rc_2012 <- combined %>%
  filter(Year==2012)

cor(rc_2012$democracy_mcmc, rc_2012$FinalCOVI)

rcplot2012 <- ggplot(rc_2012, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2012") 

ggsave("rcplot2012.png", rcplot2012, width = 6.5, height = 4, bg = "white")

#2016
rc_2016 <- combined %>%
  filter(Year==2016)

cor(rc_2016$democracy_mcmc, rc_2016$FinalCOVI)

rcplot2016 <- ggplot(rc_2016, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2016") 

ggsave("rcplot2016.png", rcplot2016, width = 6.5, height = 4, bg = "white")

#2020
rc_2020 <- combined %>%
  filter(Year==2020)

cor(rc_2020$democracy_mcmc, rc_2020$FinalCOVI)

rcplot2020 <- ggplot(rc_2020, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2020") 

ggsave("rcplot2020.png", rcplot2020, width = 6.5, height = 4, bg = "white")

#2022
rc_2022 <- combined %>%
  filter(Year==2022)

cor(rc_2022$democracy_mcmc, rc_2022$FinalCOVI)

rcplot2022 <- ggplot(rc_2022, aes(x=democracy_mcmc, y=FinalCOVI, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("Cost of Voting Index") +
  ggtitle("2022") 

ggsave("rcplot2022.png", rcplot2022, width = 6.5, height = 4, bg = "white")

################################################################

#Comparison of EDS and Voter Turnout (Figure 2 and Supplemental Information 5)

#read in VEP turnout rate data
mcdonald <- read.csv("Turnout_1980_2022_validation.csv")

#create small dataset to merge with EDS data
mcdonald_small <- mcdonald %>%
  filter(Year==2000|Year==2004|Year==2008|Year==2012|Year==2016|Year==2020|Year==2022)

#filter out unneeded observations
mcdonald_small <- mcdonald_small %>%
  filter(STATE_FULL!="United States")

mcdonald_small <- mcdonald_small %>%
  filter(STATE_FULL!="District of Columbia")

#select relevant variables
mcdonald_small <- mcdonald_small %>%
  dplyr::select(State, Year, VEP_TURNOUT_RATE, VAP_TURNOUT_RATE)

#join VEP turnout rate data with EDS data
combined <- left_join(combined, mcdonald_small, join_by(State, Year))

#correlation and plot between EDS and VEP turnout rate for each year

#2000 (Supplemental Information 5)
combined_2000 <- combined %>%
  filter(Year==2000)

cor(combined_2000$democracy_mcmc, combined_2000$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2000 <- ggplot(combined_2000, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2000") +
  ylim(.2,.8)

ggsave("mcplot2000.png", mcplot2000, width = 6.5, height = 4, bg = "white")

#2004 (Supplemental Information 5)
combined_2004 <- combined %>%
  filter(Year==2004)

cor(combined_2004$democracy_mcmc, combined_2004$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2004 <- ggplot(combined_2004, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2004") +
  ylim(.2,.8)

ggsave("mcplot2004.png", mcplot2004, width = 6.5, height = 4, bg = "white")

#2008 (Supplemental Information 5)
combined_2008 <- combined %>%
  filter(Year==2008)

cor(combined_2008$democracy_mcmc, combined_2008$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2008 <- ggplot(combined_2008, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2008") +
  ylim(.2,.8)

ggsave("mcplot2008.png", mcplot2008, width = 6.5, height = 4, bg = "white")

#2012 (Supplemental Information 5)
combined_2012 <- combined %>%
  filter(Year==2012)

cor(combined_2012$democracy_mcmc, combined_2012$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2012 <- ggplot(combined_2012, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2012") +
  ylim(.2,.8)

ggsave("mcplot2012.png", mcplot2012, width = 6.5, height = 4, bg = "white")

#2016 (Supplemental Information 5)
combined_2016 <- combined %>%
  filter(Year==2016)

cor(combined_2016$democracy_mcmc, combined_2016$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2016 <- ggplot(combined_2016, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2016") +
  ylim(.2,.8)

ggsave("mcplot2016.png", mcplot2016, width = 6.5, height = 4, bg = "white")

#2020 (Figure 2)
combined_2020 <- combined %>%
  filter(Year==2020)

cor(combined_2020$democracy_mcmc, combined_2020$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2020 <- ggplot(combined_2020, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2020") +
  ylim(.2,.8)

ggsave("mcplot2020.png", mcplot2020, width = 6.5, height = 4, bg = "white")

#2022 (Supplemental Information 5)
combined_2022 <- combined %>%
  filter(Year==2022)

cor(combined_2022$democracy_mcmc, combined_2022$VEP_TURNOUT_RATE, use = "complete.obs")

mcplot2022 <- ggplot(combined_2022, aes(x=democracy_mcmc, y=VEP_TURNOUT_RATE, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Electoral Democracy Score") +
  ylab("VEP Turnout Rate") +
  ggtitle("2022") +
  ylim(.2,.8)

ggsave("mcplot2022.png", mcplot2022, width = 6.5, height = 4, bg = "white")

#########################################################
#Figure 3: Change in Mean and SD of EDS between 2000-2022

#read in data
democracy_dataset <- read.csv("democracy_dataset.csv")

#create summary measures of mean and sd
democracy_summary <- democracy_dataset %>%
  group_by(Year) %>%
  summarize(MeanDem = mean(democracy_mcmc),
            SdDem = sd(democracy_mcmc))

#prepare for ggplot by creating separate datasets for mean and sd
democracy_summary_mean <- democracy_summary %>%
  dplyr::select(Year, MeanDem) %>%
  mutate(Type = "Mean")

democracy_summary_sd <- democracy_summary %>%
  dplyr::select(Year, SdDem) %>%
  mutate(Type = "SD")

#plot mean and sd of SDI between 2000-2022
mean_sdi_plot <- ggplot() +
  geom_line(data=democracy_summary_mean, aes(x=Year, y=MeanDem, color=Type)) +
  geom_line(data=democracy_summary_sd, aes(x=Year, y=SdDem, color=Type)) +
  scale_x_continuous(breaks = c(2000,2004,2008,2012,2016,2020,2022)) +
  scale_y_continuous(breaks = c(-1,-0.5,0,1,1.5)) +
  xlab("Year") +
  ylab("Value") +
  theme_ipsum()

ggsave("mean_sdi_plot.png", mean_sdi_plot, width = 6.5, height = 4, bg = "white")

#########################################################
#Figure 4: Change in Electoral Democracy Score by State (and Supplemental Information 6: Comparison between Change in EDS and Change in SDI)

#create summary change measure by state
democracy_change_dataset <- democracy_dataset %>%
  group_by(State) %>%
  mutate(democracy_mcmc_change = (democracy_mcmc[Year==2022] - democracy_mcmc[Year==2000])) %>%
  filter(Year==2022) %>%
  dplyr::select(State, democracy_mcmc_change)

#plot change for all 50 states between 2000-2022: Figure 4

eds_change_plot <- ggplot(democracy_change_dataset, aes(x=State, y=democracy_mcmc_change)) +
  geom_bar(stat="identity") +
  xlab("State") +
  ylab("Change in Electoral Democracy Score") +
  ggtitle("Change in Electoral Democracy Score by State, 2000-2022") +
  ylim(-2,3) +
  theme_minimal() + 
  theme(axis.text=element_text(size=6))

ggsave("eds_change_plot.png", eds_change_plot, width = 8, height = 4, bg = "white")

#Comparison between EDS Change and SDI Change (Supplemental Information 6)

#create summary dataset of change measure for SDI
democracy_change_grumbach <- grumbach %>%
  group_by(State) %>%
  mutate(democracy_mcmc_change_grumbach = (democracy_mcmc_grumbach[Year==2023] - democracy_mcmc_grumbach[Year==2000])) %>%
  filter(Year==2023) %>%
  dplyr::select(State, democracy_mcmc_change_grumbach)

#combine with EDS measure of change
combined_change <- left_join(democracy_change_dataset, democracy_change_grumbach, join_by(State))

#correlation of change in EDS and change in SDI
cor(combined_change$democracy_mcmc_change, combined_change$democracy_mcmc_change_grumbach)

eds_sdi_change <- ggplot(combined_change, aes(x=democracy_mcmc_change, y=democracy_mcmc_change_grumbach, label = State)) + 
  geom_point() +
  geom_text(hjust=0, vjust=0) +
  theme_ipsum() +
  geom_smooth(method=lm , color="gray40", se=FALSE) +
  xlab("Change in EDS, 2000-2022") +
  ylab("Change in SDI, 2000-2022") +
  ggtitle("Relationship between Change in EDS and Change in SDI, 2000-2022") +
  xlim(-3,3) +
  ylim(-3,3)

ggsave("eds_sdi_change.png", eds_sdi_change, width = 8, height = 4, bg = "white")

########################################################
#Coding of Factors and Creation of CNA Dataset for Main Results Presented in Article

#create High Improvement in Quality of Democracy (HDEM)##

#find mean and sd to establish threshold
mean(democracy_change_dataset$democracy_mcmc_change)
#0.5713074
sd(democracy_change_dataset$democracy_mcmc_change)
#0.9654393

#1/2 sd threshold
0.5713074 + (.5*(0.9654393))
#1.054027

#create binary factor
democracy_change_dataset$HDEM <- calibrate(democracy_change_dataset$democracy_mcmc_change, type = "crisp", thresholds = 1.054027)

#create final HDEM dataset
democracy_final <- democracy_change_dataset %>%
  dplyr::select(State, HDEM)

#create Strong Unions (SU)##############################
#read in union membership rates dataset
union <- read_dta("state_1983_2023.dta")

#remove DC
union <- union %>%
  filter(state2!="DC")

#filter to contemporary time period
union_filtered <- union %>%
  filter(year>=2000 & year<=2022)

#get average unionization rates by state and sector
union_sum <- union_filtered %>%
  group_by(state2, sector) %>%
  summarize(mean_pct_mem = mean(pctmem),
            sd_pct_mem = sd(pctmem))

union_summary <- union_sum %>%
  filter(sector=="Total") %>%
  dplyr::select(state2, mean_pct_mem)

#find mean and sd to establish threshold
mean(union_summary$mean_pct_mem)
#0.1076779
sd(union_summary$mean_pct_mem)
#0.05268469

#1/2 sd threshold
0.1076779 + (.5*(0.05268469))
#0.1340202

#create binary SU factor
union_summary$SU <- calibrate(union_summary$mean_pct_mem, type = "crisp", thresholds = 0.1340202)

#create variable label for join and ungroup
union_summary <- union_summary %>%
  mutate(State = state2)

union_summary <- ungroup(union_summary)

#create final SU dataset
union_final <- union_summary %>%
  dplyr::select(State, SU)

#Create High Democratic Control (HDC)###################

#read in dataset
dems_unified <- read.csv("dems_unified_control_count_revised.csv")

#find threshold for HDC
#1/2 sd threshold
mean(dems_unified$UnifiedDemProp)
#0.2252174
sd(dems_unified$UnifiedDemProp)
#0.2527103

#find threshold
0.2252174 + 0.5*(0.2527103)
#0.3515725

#create binary factor for HDC
dems_unified$HDC <- calibrate(dems_unified$UnifiedDemProp, type = "crisp", thresholds = 0.3515725)

#create final dataset
dems_final <- dems_unified %>%
  dplyr::select(State, HDC)

#Create High People of Color (HPOC)#####################
race <- read.csv("race.csv")

#remove DC
race <- race %>%
  filter(State!="District of Columbia")

#create racial proportion variables
race <- race %>%
  mutate(PoCProp = (Native+Asian+Black+Latinx)/Total)

#summarize by state
race_summary <- race %>%
  group_by(State) %>%
  summarize(PoC_Mean = mean(PoCProp),
            PoC_SD = sd(PoCProp) )

#find mean and sd to identify threshold
mean(race_summary$PoC_Mean)
#0.2730533
sd(race_summary$PoC_Mean)
#0.1519612

#find threshold
0.2730533 + (.5*(0.1519612))
#0.3490339

#create binary factor
race_summary$HPOC <- calibrate(race_summary$PoC_Mean, type = "crisp", thresholds = 0.3490339)

#create final dataset
race_final <- race_summary %>%
  dplyr::select(State, HPOC)

#Liberal Democratic Party (LDEM)###############################
dems <- read_dta("shor mccarty 1993-2020 state aggregate data April 2023 release.dta")

#filter to relevant years
dems <- dems %>%
  filter(year>=2000 & year<=2022)

#summary dataset
dems_summary <- dems %>%
  group_by(st) %>%
  summarize(mean_sen_dems = mean(sen_dem_mean, na.rm=TRUE),
            sd_sen_dems = sd(sen_dem_mean, na.rm=TRUE))

#find mean and sd to identify threshold
mean(dems_summary$mean_sen_dems, na.rm=TRUE)
#-0.7901677
sd(dems_summary$mean_sen_dems, na.rm=TRUE)
#0.3558145

#find threshold
-0.7901677 - (.5*(0.3558145))
#-0.9680749

#create binary factor
liberal_dems_final <- dems_summary %>%
  mutate(LDEM = if_else(mean_sen_dems< -0.9680749,1,0))

#create final LDEM dataset
liberal_dems_final <- liberal_dems_final %>%
  mutate(State = st) %>%
  dplyr::select(State, LDEM)

#Liberal Public Mood (LM)################################

#read in data
mood <- read_dta("LagodnyJonesKochEnns_MainAnalysis.dta")

#filter years
mood <- mood %>%
  filter(year>=2000)

#drop DC
mood <- mood %>%
  filter(cstate_initial!="DC")

#summary by state
mood_summary <- mood %>%
  group_by(cstate_initial) %>%
  summarize(mean_mood = mean(LJKE_StatePolicyMood),
            sd_mood = sd(LJKE_StatePolicyMood))

#1/2 sd threshold
mean(mood_summary$mean_mood)
#0.4625305
sd(mood_summary$mean_mood)
#0.06645155

#find threshold
0.4625305 + (.5*(0.06645155))
#0.4957563

#create factor
mood_summary <- mood_summary %>%
  mutate(LM = if_else(mean_mood > 0.4957563, 1, 0))

#create final dataset
mood_final <- mood_summary %>%
  mutate(State = cstate_initial) %>%
  dplyr::select(State, LM)

#########################################################
#Coincidence Analysis: Main Results Presented in Article

#join binary factor datasets to create cna dataset for analysis
cna_data <- left_join(democracy_final, dems_final, join_by(State))
cna_data <- left_join(cna_data, liberal_dems_final, join_by(State))
cna_data <- left_join(cna_data, mood_final, join_by(State))
cna_data <- left_join(cna_data, union_final, join_by(State))
cna_data <- left_join(cna_data, race_final, join_by(State))

#ungroup to enable selection of factors for analysis
cna_data <- ungroup(cna_data)

#select factors for analysis
cna_data <- cna_data %>%
  dplyr::select(HDEM, HDC, LDEM, LM, SU, HPOC)

#run cna with frscored
frscored_cna(cna_data, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#write solution to csv file for presentation in manuscript and supplemental information
#first, save as object (note model is same as above)
cna <- frscored_cna(cna_data, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna[["rean_models"]], "cna-solution.csv")

#create causal hypergraph for presentation in manuscript
x <- "HDC*lm+SU*HPOC+LDEM*LM*SU<->HDEM"
causal_hyper_graph <- causalHyperGraph(x)
saveRDS(causal_hyper_graph, file = "my_causal_hypergraph.rds")
#the causal hypergraph is saved as an rds file; call the object to open in R Studio

#########################################################
#Supplemental Information 7: Ideology and Support for Policies that Strengthen Electoral Democracy Among Democrats

#Part 1: Analysis of MA Legislators Roll-Call Vote on EDR

#load ideology estimates from Shor-McCarty dataset
smd <- read_dta("shor mccarty 1993-2022 individual legislator data January 2025 release.dta")

#limit to Massachusetts Democrats in 2022 house
MAdems <- smd %>%
  filter(st=="MA" & party=="D" & house2022==1) %>%
  dplyr::select(name, np_score)

#write to csv. Some names from smd have discrepancies and need to be manually edited to align correctly with names in roll-call dataset
write.csv(MAdems, "MAdems.csv")

#ingest MAdems data with aligned names
MAdemsEdited <- read.csv("MAdems-Edited.csv")

#read in roll-call vote on SDR amendment (HRC135)
hrc135 <- read.csv("HRC135.csv")

#join datasets
joined <- left_join(hrc135, MAdemsEdited, join_by("Name"))

#estimate logistic regression model 
MA_rollcall_model <- glm(data=joined, Vote ~ NP_Score, family = "binomial")

#output model results in word document to folder
wordreg(MA_rollcall_model,
        file = "EDR-model.docx",
        stars = c(0.001, 0.01, 0.05),
        digits = 2)

#estimate marginal effect on predicted probability 
ggpredict(MA_rollcall_model, terms = "NP_Score")

#Part 2: Effect of Ideology of Democrats on Quality of Electoral Democracy

#load Grumbach data
grumbach2 <- read.csv("SDI_2.0.csv")

#load updated party control data
partycontrol <- read.csv("dem-control.csv")

#load updated legislator ideology data
demsideology <- read_dta("shor mccarty 1993-2022 state aggregate data January 2025 release.dta")

#limit datasets to same years
grumbach2 <- grumbach2 %>%
  filter(Year>=2000 & Year<=2022)

partycontrol <- partycontrol %>%
  filter(Year>=2000 & Year<=2022)

demsideology <- demsideology %>%
  filter(year>=2000 & year<=2022)

#get same labels for matching variables
demsideology <- demsideology %>%
  mutate(Year = year,
         State = st)

#select variables of interest from each dataset
grumbachF <- grumbach2 %>%
  dplyr::select(State, Year, democracy_mcmc_grumbach)

partycontrolF <- partycontrol %>%
  dplyr::select(State, Year, ranney4_control)

demsideologyF <- demsideology %>%
  dplyr::select(State, Year, sen_dem, hou_dem)

#join datasets to prepare for analysis
joined2 <- left_join(grumbachF, partycontrolF, join_by("State", "Year"))
joined2 <- left_join(joined2, demsideologyF, join_by("State", "Year"))

##create variable where 1 = Dem control, and 0=divided OR Rep control
joined2 <- joined2 %>%
  mutate(DemControl = if_else(ranney4_control==1,1,0))

#estimate difference in difference models with interaction terms
model_interaction_sen <- lm(data=joined2, democracy_mcmc_grumbach ~ DemControl*sen_dem + factor(State) + factor(Year))

model_interaction_hou <- lm(data=joined2, democracy_mcmc_grumbach ~ DemControl*hou_dem + factor(State) + factor(Year))

#save interaction models to word file
#note: need to manually remove fixed effects for states and years
wordreg(l=list(model_interaction_sen, model_interaction_hou),
        file = "DiD-model.docx",
        stars = c(0.001, 0.01, 0.05),
        digits = 2)

#basic model with only unified Dem control as predictor
model_basic <- lm(data=joined2, democracy_mcmc_grumbach ~ DemControl + factor(State) + factor(Year))

#save word document with basic model
#note: need to manually remove fixed effects for states and years
wordreg(model_basic,
        file = "DiD-model-basic.docx",
        stars = c(0.001, 0.01, 0.05),
        digits = 2)

########################################################
#SI 11: Robustness Tests: Altering Cutpoints for Inclusion in Factors

#Note: There are 12 robustness tests in all. In each test, we adjust one factor up or down, and leave others constant. After each test, we save results to csv file for later compilation. 

#Robustness test 1: Lower threshold for HDEM (HDEML)

#establish lower threshold for HDEML
mean(democracy_change_dataset$democracy_mcmc_change)
#0.5713074
sd(democracy_change_dataset$democracy_mcmc_change)
#0.9654393

#.3 sd threshold
0.5713074 + (.3*(0.9654393))
#0.8609392

#create threshold variable
democracy_change_dataset$HDEML <- calibrate(democracy_change_dataset$democracy_mcmc_change, type = "crisp", thresholds = 0.8609392)

#create final democracy HDEML dataset
democracy_final_low <- democracy_change_dataset %>%
  dplyr::select(State, HDEML)

#create joined dataset for cna
cna_data_HDEML <- left_join(democracy_final_low, dems_final, join_by(State))
cna_data_HDEML <- left_join(cna_data_HDEML, liberal_dems_final, join_by(State))
cna_data_HDEML <- left_join(cna_data_HDEML, mood_final, join_by(State))
cna_data_HDEML <- left_join(cna_data_HDEML, union_final, join_by(State))
cna_data_HDEML <- left_join(cna_data_HDEML, race_final, join_by(State))

#ungroup
cna_data_HDEML <- ungroup(cna_data_HDEML)

#select final dataset for analysis
cna_data_HDEML <- cna_data_HDEML %>%
  dplyr::select(HDEML, HDC, LDEM, LM, SU, HPOC)

#run cna and save results to csv
cna_HDEML <- frscored_cna(cna_data_HDEML, outcome = "HDEML", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HDEML[["rean_models"]], "cna-solution_HDEML.csv")

#Robustness Test #2: Raised threshold for HDEM (HDEMH)

#note mean and sd from Robustness Test #1

#.7 sd threshold
0.5713074 + (.7*(0.9654393))
#1.247115

#create threshold factor
democracy_change_dataset$HDEMH <- calibrate(democracy_change_dataset$democracy_mcmc_change, type = "crisp", thresholds = 1.247115)

#create final democracy HDEMH dataset
democracy_final_high <- democracy_change_dataset %>%
  dplyr::select(State, HDEMH)

#create joined dataset for cna
cna_data_HDEMH <- left_join(democracy_final_high, dems_final, join_by(State))
cna_data_HDEMH <- left_join(cna_data_HDEMH, liberal_dems_final, join_by(State))
cna_data_HDEMH <- left_join(cna_data_HDEMH, mood_final, join_by(State))
cna_data_HDEMH <- left_join(cna_data_HDEMH, union_final, join_by(State))
cna_data_HDEMH <- left_join(cna_data_HDEMH, race_final, join_by(State))

#ungroup
cna_data_HDEMH <- ungroup(cna_data_HDEMH)

#select final dataset for analysis
cna_data_HDEMH <- cna_data_HDEMH %>%
  dplyr::select(HDEMH, HDC, LDEM, LM, SU, HPOC)

#run cna and save results to csv
cna_HDEMH <- frscored_cna(cna_data_HDEMH, outcome = "HDEMH", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HDEMH[["rean_models"]], "cna-solution_HDEMH.csv")

#Robustness Test #3: Lowered Threshold of High Democratic Control (LOWDC)

mean(dems_unified$UnifiedDemProp)
#0.2286957
sd(dems_unified$UnifiedDemProp)
#0.2502743

#.3 sd threshold
0.2286957 + 0.3*(0.2502743)
#0.303778

#create threshold
dems_unified$LOWDC <- calibrate(dems_unified$UnifiedDemProp, type = "crisp", thresholds = 0.303778)

#create final dataset
dems_final_LOWDC <- dems_unified %>%
  dplyr::select(State, LOWDC)

#create joined dataset for cna
cna_data_LOWDC <- left_join(democracy_final, dems_final_LOWDC, join_by(State))
cna_data_LOWDC <- left_join(cna_data_LOWDC, liberal_dems_final, join_by(State))
cna_data_LOWDC <- left_join(cna_data_LOWDC, mood_final, join_by(State))
cna_data_LOWDC <- left_join(cna_data_LOWDC, union_final, join_by(State))
cna_data_LOWDC <- left_join(cna_data_LOWDC, race_final, join_by(State))

#ungroup
cna_data_LOWDC <- ungroup(cna_data_LOWDC)

#select final dataset for analysis
cna_data_LOWDC <- cna_data_LOWDC %>%
  dplyr::select(HDEM, LOWDC, LDEM, LM, SU, HPOC)

#run cna and save results to csv
cna_LOWDC <- frscored_cna(cna_data_LOWDC, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LOWDC[["rean_models"]], "cna-solution_LOWDC.csv")

#Robustness Test #4: Raised Threshold of High Democratic Control (HIDC)

#raised threshold
0.2286957 + 0.7*(0.2502743)
#0.4038877

#create raised threshold
dems_unified$HIDC <- calibrate(dems_unified$UnifiedDemProp, type = "crisp", thresholds = 0.4038877)

#create HIDC dataset
dems_final_HIDC <- dems_unified %>%
  dplyr::select(State, HIDC)

#create joined dataset for cna
cna_data_HIDC <- left_join(democracy_final, dems_final_HIDC, join_by(State))
cna_data_HIDC <- left_join(cna_data_HIDC, liberal_dems_final, join_by(State))
cna_data_HIDC <- left_join(cna_data_HIDC, mood_final, join_by(State))
cna_data_HIDC <- left_join(cna_data_HIDC, union_final, join_by(State))
cna_data_HIDC <- left_join(cna_data_HIDC, race_final, join_by(State))

#ungroup
cna_data_HIDC <- ungroup(cna_data_HIDC)

#select final dataset for analysis
cna_data_HIDC <- cna_data_HIDC %>%
  dplyr::select(HDEM, HIDC, LDEM, LM, SU, HPOC)

#run cna and save results to csv
cna_HIDC <- frscored_cna(cna_data_HIDC, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HIDC[["rean_models"]], "cna-solution_HIDC.csv")

#Robustness Test #5: Lowered Threshold of High Union Strength (LOSU)

#identify threshold
mean(union_summary$mean_pct_mem)
#0.1076779
sd(union_summary$mean_pct_mem)
#0.05268469

#.3 sd threshold
0.1076779 + (.3*(0.05268469))
#0.1234833

#create binary factor
union_summary$LOSU <- calibrate(union_summary$mean_pct_mem, type = "crisp", thresholds = 0.1234833)

#ungroup
union_summary <- ungroup(union_summary)

#create final LOSU dataset
union_final_LOSU <- union_summary %>%
  dplyr::select(State, LOSU)

#create joined dataset for cna
cna_data_LOSU <- left_join(democracy_final, dems_final, join_by(State))
cna_data_LOSU <- left_join(cna_data_LOSU, liberal_dems_final, join_by(State))
cna_data_LOSU <- left_join(cna_data_LOSU, mood_final, join_by(State))
cna_data_LOSU <- left_join(cna_data_LOSU, union_final_LOSU, join_by(State))
cna_data_LOSU <- left_join(cna_data_LOSU, race_final, join_by(State))

#ungroup
cna_data_LOSU <- ungroup(cna_data_LOSU)

#select final dataset for analysis
cna_data_LOSU <- cna_data_LOSU %>%
  dplyr::select(HDEM, HDC, LDEM, LM, LOSU, HPOC)

#run cna and save results to csv
cna_LOSU <- frscored_cna(cna_data_LOSU, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LOSU[["rean_models"]], "cna-solution_LOSU.csv")

#Robustness Test #6: Raised Threshold for Strong Unions (HISU)

#.7 sd threshold
0.1076779 + (.7*(0.05268469))
#0.1445572

#create binary factor
union_summary$HISU <- calibrate(union_summary$mean_pct_mem, type = "crisp", thresholds = 0.1445572)

#create final HISU dataset
union_final_HISU <- union_summary %>%
  ungroup() %>%
  dplyr::select(State, HISU)

#create joined dataset for cna
cna_data_HISU <- left_join(democracy_final, dems_final, join_by(State))
cna_data_HISU <- left_join(cna_data_HISU, liberal_dems_final, join_by(State))
cna_data_HISU <- left_join(cna_data_HISU, mood_final, join_by(State))
cna_data_HISU <- left_join(cna_data_HISU, union_final_HISU, join_by(State))
cna_data_HISU <- left_join(cna_data_HISU, race_final, join_by(State))

#ungroup
cna_data_HISU <- ungroup(cna_data_HISU)

#select final dataset for analysis
cna_data_HISU <- cna_data_HISU %>%
  dplyr::select(HDEM, HDC, LDEM, LM, HISU, HPOC)

#run cna and save results to csv. Note con/cov>.70 to get model results
cna_HISU <- frscored_cna(cna_data_HISU, outcome = "HDEM", fit.range = c(.70,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HISU[["rean_models"]], "cna-solution_HISU.csv")

#Robustness Test #7: Lowered Threshold of High People of Color (HPOCL)

#find mean and sd to identify threshold
mean(race_summary$PoC_Mean)
#0.2730533
sd(race_summary$PoC_Mean)
#0.1519612

#create threshold
0.2730533 + (.3*(0.1519612))
#0.3186417

#create threshold factor
race_summary <- race_summary %>%
  mutate(HPOCL = if_else(PoC_Mean > 0.3186417,1,0))

#final HPOCL dataset
race_final_low <- race_summary %>%
  dplyr::select(State, HPOCL)

#create joined dataset
cna_data_HPOCL <- left_join(democracy_final, dems_final, join_by(State))
cna_data_HPOCL <- left_join(cna_data_HPOCL, liberal_dems_final, join_by(State))
cna_data_HPOCL <- left_join(cna_data_HPOCL, mood_final, join_by(State))
cna_data_HPOCL <- left_join(cna_data_HPOCL, union_final, join_by(State))
cna_data_HPOCL <- left_join(cna_data_HPOCL, race_final_low, join_by(State))

#ungroup
cna_data_HPOCL <- ungroup(cna_data_HPOCL)

#select final dataset for analysis
cna_data_HPOCL <- cna_data_HPOCL %>%
  dplyr::select(HDEM, HDC, LDEM, LM, SU, HPOCL)

#run cna and save results 
cna_HPOCL <- frscored_cna(cna_data_HPOCL, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HPOCL[["rean_models"]], "cna-solution_HPOCL.csv")

#Robustness Test #8: Raised Threshold for High Population of People of Color (HPOCH)

#use mean and sd from above

#create threshold
0.2730533 + (.7*(0.1519612))
#0.3794261

#create threshold variable
race_summary <- race_summary %>%
  mutate(HPOCH = if_else(PoC_Mean > 0.3794261,1,0))

#final HPOCH dataset
race_final_high <- race_summary %>%
  dplyr::select(State, HPOCH)

#create joined dataset
cna_data_HPOCH <- left_join(democracy_final, dems_final, join_by(State))
cna_data_HPOCH <- left_join(cna_data_HPOCH, liberal_dems_final, join_by(State))
cna_data_HPOCH <- left_join(cna_data_HPOCH, mood_final, join_by(State))
cna_data_HPOCH <- left_join(cna_data_HPOCH, union_final, join_by(State))
cna_data_HPOCH <- left_join(cna_data_HPOCH, race_final_high, join_by(State))

#ungroup
cna_data_HPOCH <- ungroup(cna_data_HPOCH)

#select final dataset for analysis
cna_data_HPOCH <- cna_data_HPOCH %>%
  dplyr::select(HDEM, HDC, LDEM, LM, SU, HPOCH)

#run cna and save results 
cna_HPOCH <- frscored_cna(cna_data_HPOCH, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_HPOCH[["rean_models"]], "cna-solution_HPOCH.csv")

#Robustness Test #9: Lowered Threshold of Liberal Democrats (LDEML)

mean(dems_summary$mean_sen_dems, na.rm=TRUE)
#-0.7901677
sd(dems_summary$mean_sen_dems, na.rm=TRUE)
#0.3558145

#find threshold
-0.7901677 - (.3*(0.3558145))
#-0.8969121

#create lowered threshold variable
liberal_dems_final_low <- dems_summary %>%
  mutate(LDEML = if_else(mean_sen_dems < -0.8969121, 1, 0 ))

#create final liberal dems dataset
liberal_dems_final_low <- liberal_dems_final_low %>%
  mutate(State = st) %>%
  dplyr::select(State, LDEML)

#create joined dataset
cna_data_LDEML <- left_join(democracy_final, dems_final, join_by(State))
cna_data_LDEML <- left_join(cna_data_LDEML, liberal_dems_final_low, join_by(State))
cna_data_LDEML <- left_join(cna_data_LDEML, mood_final, join_by(State))
cna_data_LDEML <- left_join(cna_data_LDEML, union_final, join_by(State))
cna_data_LDEML <- left_join(cna_data_LDEML, race_final, join_by(State))

#ungroup
cna_data_LDEML <- ungroup(cna_data_LDEML)

#select final dataset for analysis
cna_data_LDEML <- cna_data_LDEML %>%
  dplyr::select(HDEM, HDC, LDEML, LM, SU, HPOC)

#run cna and save results to csv
cna_LDEML <- frscored_cna(cna_data_LDEML, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LDEML[["rean_models"]], "cna-solution_LDEML.csv")

#Robustness Test #10: Raised Threshold for Liberal Democratic Party (LDEMH)

mean(dems_summary$mean_sen_dems, na.rm=TRUE)
#-0.7901677
sd(dems_summary$mean_sen_dems, na.rm=TRUE)
#0.3558145

#find threshold
-0.7901677 - (.7*(0.3558145))
#-1.039238

#create raised threshold variable
liberal_dems_final_high <- dems_summary %>%
  mutate(LDEMH = if_else(mean_sen_dems < -1.039238, 1, 0 ))

#create final liberal dems dataset
liberal_dems_final_high <- liberal_dems_final_high %>%
  mutate(State = st) %>%
  dplyr::select(State, LDEMH)

#create joined dataset
cna_data_LDEMH <- left_join(democracy_final, dems_final, join_by(State))
cna_data_LDEMH <- left_join(cna_data_LDEMH, liberal_dems_final_high, join_by(State))
cna_data_LDEMH <- left_join(cna_data_LDEMH, mood_final, join_by(State))
cna_data_LDEMH <- left_join(cna_data_LDEMH, union_final, join_by(State))
cna_data_LDEMH <- left_join(cna_data_LDEMH, race_final, join_by(State))

#ungroup
cna_data_LDEMH <- ungroup(cna_data_LDEMH)

#select final dataset for analysis
cna_data_LDEMH <- cna_data_LDEMH %>%
  dplyr::select(HDEM, HDC, LDEMH, LM, SU, HPOC)

#run cna and save results to csv
cna_LDEMH <- frscored_cna(cna_data_LDEMH, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LDEMH[["rean_models"]], "cna-solution_LDEMH.csv")

#Robustness Test #11: Lowered Threshold for Liberal Mood (LMLO)

mean(mood_summary$mean_mood)
#0.4625305
sd(mood_summary$mean_mood)
#0.06645155

#threshold for LMLO
0.4625305 + (.3*(0.06645155))
#0.482466

#create threshold variable for LMLO
mood_final_low <- mood_summary %>%
  mutate(State = cstate_initial) %>%
  mutate(LMLO = if_else(mean_mood > 0.482466, 1, 0))

#create final LMLO dataset
mood_final_low <- mood_final_low %>%
  dplyr::select(State, LMLO)

#create joined dataset
cna_data_LMLO <- left_join(democracy_final, dems_final, join_by(State))
cna_data_LMLO <- left_join(cna_data_LMLO, liberal_dems_final, join_by(State))
cna_data_LMLO <- left_join(cna_data_LMLO, mood_final_low, join_by(State))
cna_data_LMLO <- left_join(cna_data_LMLO, union_final, join_by(State))
cna_data_LMLO <- left_join(cna_data_LMLO, race_final, join_by(State))

#ungroup
cna_data_LMLO <- ungroup(cna_data_LMLO)

#select final dataset for analysis
cna_data_LMLO <- cna_data_LMLO %>%
  dplyr::select(HDEM, HDC, LDEM, LMLO, SU, HPOC)

#run cna and save results to csv
cna_LMLO <- frscored_cna(cna_data_LMLO, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LMLO[["rean_models"]], "cna-solution_LMLO.csv")

#Robustness Test #12: Raised Threshold for Liberal Mood (LMHI)

mean(mood_summary$mean_mood)
#0.4625305
sd(mood_summary$mean_mood)
#0.06645155

#threshold for LMLO
0.4625305 + (.7*(0.06645155))
#0.5090466

#create threshold variable for LMLO
mood_final_high <- mood_summary %>%
  mutate(State = cstate_initial) %>%
  mutate(LMHI = if_else(mean_mood > 0.5090466, 1, 0))

#create final LMHI dataset
mood_final_high <- mood_final_high %>%
  dplyr::select(State, LMHI)

#create joined dataset
cna_data_LMHI <- left_join(democracy_final, dems_final, join_by(State))
cna_data_LMHI <- left_join(cna_data_LMHI, liberal_dems_final, join_by(State))
cna_data_LMHI <- left_join(cna_data_LMHI, mood_final_high, join_by(State))
cna_data_LMHI <- left_join(cna_data_LMHI, union_final, join_by(State))
cna_data_LMHI <- left_join(cna_data_LMHI, race_final, join_by(State))

#ungroup
cna_data_LMHI <- ungroup(cna_data_LMHI)

#select final dataset for analysis
cna_data_LMHI <- cna_data_LMHI %>%
  dplyr::select(HDEM, HDC, LDEM, LMHI, SU, HPOC)

#run cna and save results to csv
cna_LMHI <- frscored_cna(cna_data_LMHI, outcome = "HDEM", fit.range = c(.75,1), granularity = 0.01, what = "all")

#then, write solutions and summary statistics to csv
write.csv(cna_LMHI[["rean_models"]], "cna-solution_LMHI.csv")

#NOTE: there is no automated functionality for identifying
#submodel or supermodel relations. Users must manually 
#inspect the results of the most fit-robust model for each
#robustness test, compare it to the results of the main model,
#and determine whether submodel, supermodel, or no relations exist.
#Users can then manually combine the tables to create the final table for Supplemental Information 11.

#######################################################
#Supplemental Information 12: Robustness Tests: Using Grumbach’s SDI to Measure High Improvement in the Quality of Electoral Democracy

democracy_change_grumbach2 <- grumbach %>%
  group_by(State) %>%
  mutate(democracy_mcmc_change_grumbach = (democracy_mcmc_grumbach[Year==2022] - democracy_mcmc_grumbach[Year==2000])) %>%
  filter(Year==2022) %>%
  dplyr::select(State, democracy_mcmc_change_grumbach)

mean(democracy_change_grumbach2$democracy_mcmc_change_grumbach)
#-0.2618357

sd(democracy_change_grumbach2$democracy_mcmc_change_grumbach)
#0.9519846

#1/2 sd threshold
-0.2618357 + 0.5*(0.9519846)
#0.2141566

#create threshold variable
democracy_change_grumbach2$HDEMG <- calibrate(democracy_change_grumbach$democracy_mcmc_change_grumbach, type = "crisp", thresholds = 0.2141566)

#create final HDEMG dataset
democracy_change_grumbach_final2 <- democracy_change_grumbach2 %>%
  dplyr::select(State, HDEMG)

#join datasets
cna_data_G <- left_join(democracy_change_grumbach_final2, dems_final, join_by(State))
cna_data_G <- left_join(cna_data_G, liberal_dems_final, join_by(State))
cna_data_G <- left_join(cna_data_G, mood_final, join_by(State))
cna_data_G <- left_join(cna_data_G, union_final, join_by(State))
cna_data_G <- left_join(cna_data_G, race_final, join_by(State))

#ungroup
cna_data_G <- ungroup(cna_data_G)

#create final dataset for analysis
cna_data_G <- cna_data_G %>%
  dplyr::select(HDEMG, HDC, LDEM, LM, SU, HPOC)

#run cna with Grumbach-based outcome measure
frscored_cna(cna_data_G, outcome = "HDEMG", fit.range = c(.75,1), granularity = 0.01, what = "all", print.all=TRUE)

#create saved object result
cna_result_G <- frscored_cna(cna_data_G, outcome = "HDEMG", fit.range = c(.75,1), granularity = 0.01, what = "all", print.all=TRUE)

#write solution to csv
write.csv(cna_result_G[["rean_models"]], "cna-solution_G.csv")

#create causal hypergraph
xG <- "LDEM+LM*SU<->HDEMG"

causal_hyper_graph_G <- causalHyperGraph(xG)
saveRDS(causal_hyper_graph_G, file = "my_causal_hypergraph_G.rds")

