#!/usr/bin/env Rscript
library(ggplot2)
library(dplyr)
library(hash)
require(scales)
my_path <- getwd()
setwd(my_path)
files<-list.files("./data/",pattern = "*", full.names = TRUE, ignore.case = TRUE)
for (f in files){
tc = read.csv(f,stringsAsFactors=FALSE)
tc$nomDependencia[tc$test_id == 0] <- "Otro"
temas<-unique(tc$test_id)
#print(temas)
tema_correcto<-hash()
tema_error1<-hash()
tema_error2<-hash()
pureza<-hash()
nomtema<-hash()
for (i in temas){
  a<-toString(i)
  nomtema[a]<-unique(tc$nomDependencia[tc$test_id==i])
  all_by_topic<-sum(tc$test_id==i)
  all_in_tc<-sum(tc$test_id>-1)
  # H0 true and accepted
  tema_correcto[a]<-sum(tc$test_id==tc$dependencia_id & tc$test_id==i)/all_by_topic
  #H0 true, but rejected
  tema_error1[a]<-sum(tc$test_id!=tc$dependencia_id & tc$test_id==i)/all_by_topic
  #H0 false, but accetped
  tema_error2[a]<-sum(tc$test_id!=tc$dependencia_id & tc$dependencia_id==i)/all_in_tc
  pureza[a]<-sum(tc$test_id==tc$dependencia_id & tc$test_id==i)/(0.000001+sum(tc$test_id!=tc$dependencia_id & tc$dependencia_id==i)+sum(tc$test_id==tc$dependencia_id & tc$test_id==i))
}
temas<-keys(tema_correcto)
tema_correcto<-values(tema_correcto)
tema_noselec<-values(tema_error1)
error_tema<-values(tema_error2)
pureza<-values(pureza)

nomtema<-values(nomtema)
df<-data.frame(temas,nomtema,tema_correcto,tema_noselec,error_tema,pureza, stringsAsFactors=FALSE)

df<-df[with(df, order(-tema_correcto, -pureza)), ]
my_line<-sprintf("%f,%s",sum(head(sort(df$pureza,decreasing=TRUE),n=5)), f)
write(my_line,file="opt.csv",append=TRUE)

p <- ggplot(df, aes(tema_correcto, pureza))
p <- p +geom_point(aes(colour = factor(nomtema),shape = factor(nomtema)),size=6)
p <- p +scale_y_continuous(labels=percent,breaks = round(seq(0, 1, by = 0.1),1))
p <- p +scale_x_continuous(labels=percent,breaks = round(seq(0, 1, by = 0.1),1))
p <- p + coord_cartesian(ylim=c(-0.02,1),xlim=c(-0.02,1))
p <- p + scale_shape_manual(values = 0:length(unique(df$nomtema)))
p <- p + ylab("Solicitudes etiquetadas que realmente pertenecen al tema (Pureza)")
p <- p + xlab("Fraccion de soliccitudes del tema que fueron etiquetadas con la etiqueta del tema (Eficiencia)")
p <- p + labs("Clasificador version0, eficiencia y pureza del clasificador en la muestra de prueba")


plot_file<-gsub("csv","pdf",gsub("data","plots",f))
ggsave(plot_file,width = 16, height = 7, dpi = 120)
}


