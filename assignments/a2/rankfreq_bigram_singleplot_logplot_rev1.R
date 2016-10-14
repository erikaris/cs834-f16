require(ggplot2)

mydata1 <- read.csv("rank_freq.csv", head=TRUE, sep = ',')
mydata2 <- read.csv("rank_freq_bigram.csv", head=TRUE, sep = ',')

ggplot(data=mydata1, aes(x=rank, y=prob)) + geom_line(data=mydata1, aes(x=rank, y=prob, color="Frequency")) + geom_line(data=mydata2, aes(x=rank, y=prob, color="Bigram")) + scale_colour_manual(name='', values=c('Frequency'='#000099', 'Bigram'='#CC0000'), guide='legend')
