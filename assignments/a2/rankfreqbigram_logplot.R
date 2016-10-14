require(ggplot2)

mydata <- read.csv("/home/erikaris/PycharmProjects/IR-A2/rank_freq_bigram.csv", head=TRUE, sep = ',')
ggplot(data=mydata, aes(x=rank, y=prob)) + geom_point() + scale_x_log10() + scale_y_log10()
#ggplot(data=mydata, aes(x=rank, y=prob)) + geom_point() + scale_x_log10() + scale_y_log10()


