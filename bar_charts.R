#!/usr/bin/env Rscript
library(ggplot2)
library(dplyr)
setwd('~/ws/atencion/mynltk')
total = read.csv("total_peticiones.csv") 
df<-mutate(total, cumulative=cumsum(fraction))
top10<-head(df,10)
order<-top10$nomTema.nomsubtema
order
p <- ggplot(data=top10, aes(nomTema.nomsubtema))
p <- p+geom_bar(aes(y=fraction),stat="identity",color="red",fill="red")+ scale_x_discrete(limits = order)
p <- p+geom_point(aes(y=cumulative),shape=1,size=5,color = "blue")
p <- p+geom_line(aes(y=cumulative),linetype="dashed",size=2)
p <- p+theme(axis.text.x = element_text(angle = 37, hjust = 0.65))
p <- p+theme(axis.text.x=element_text(size=9),
        axis.title=element_text(size=14,face="bold"))
p <- p+labs(y = "Fraccion/Fraccion Acumulada")+ expand_limits(y=c(0,0.6))
p <- p+labs(x = "Tema de la petición")
p <- p+ggtitle("Fracción de peticiones TOTALES")
ggsave("peticiones_totales.pdf",width = 16, height = 7, dpi = 120)

portal = read.csv("portal_peticiones.csv") 
df<-mutate(portal, cumulative=cumsum(fraction))
top10<-head(df,10)
order<-top10$nomTema.nomsubtema
order
p <- ggplot(data=top10, aes(nomTema.nomsubtema))
p <- p+geom_bar(aes(y=fraction),stat="identity",color="red",fill="red")+ scale_x_discrete(limits = order)
p <- p+geom_point(aes(y=cumulative),shape=1,size=5,color = "blue")
p <- p+geom_line(aes(y=cumulative),linetype="dashed",size=2)
p <- p+theme(axis.text.x = element_text(angle = 37, hjust = 0.65))
p <- p+theme(axis.text.x=element_text(size=9),
             axis.title=element_text(size=14,face="bold"))
p <- p+labs(y = "Fraccion/Fraccion Acumulada")+ expand_limits(y=c(0,0.6))
p <- p+labs(x = "Tema de la petición")
p <- p+ggtitle("Fracción de peticiones en PORTAL")
ggsave("peticiones_portal.pdf",width = 16, height = 7, dpi = 120)
