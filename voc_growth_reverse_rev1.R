require(ggplot2)

mydata <- read.csv("4_2-voc_corpus_reverse_rev1.csv", head=TRUE, sep = ',')
x <- mydata$corpus_size
y <- mydata$vocabulary_size

#model
fit<-nls(y~k*(x^b), data = mydata, start = list(k=1,b=1))
summary(fit)
#get some estimation of goodness of fit
cor(y, predict(fit))

ggplot(data=mydata, aes(x=corpus_size, y=vocabulary_size))  + geom_line(aes(group = 1, color="Actual")) + geom_line(data=mydata, aes(x=corpus_size, y=predict(fit), color="Heaps")) + labs(title='Vocabulary Growth for Wikipedia documents (reversed order)',x = 'Corpus Size', y = 'Vocabulary Size') + scale_colour_manual(name='', values=c('Actual'='#000099', 'Heaps'='#CC0000'), guide='legend')

