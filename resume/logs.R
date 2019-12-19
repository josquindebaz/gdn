#library(tcltk)
#x11()

D <- read.csv(file="lengthOpens.csv", header=TRUE, sep=",")

svg(filename="Q_166.svg")
matplot (D[, 1], D[46], type='l', xlim=c(0,500), col="Magenta" ,
    xlab="Nombre de mots", ylab="Nombre de réponses",
    main = "166 Pour quelle(s) politique(s) publique(s) ou pour quels domaines
    d'action publique, seriez-vous prêts à payer plus d'impôts ?"
    )


svg(filename="nwords.svg",
    width=15, 
    height=90, 
    pointsize=12)

par( mfrow = c(61, 2), mar=c(2, 2, 2, 2) )
for (d in 2:73)  { 
#for (d in 2:26)  { 
    matplot (D[, 1], D[d], type='l', 
    xlab=NA,  xlim=c(0,500),
    ylab=NA, 
    main=colnames(D)[d], #col=palette()[sample(1:8, 1)] 
    col="Magenta"
    )  
}

svg(filename="logs.svg",
    width=15, 
    height=30, 
    pointsize=10)

par( mfrow = c(21, 4), mar=c(2, 2, 2, 2) )
#for (d in 2:26)  { 
for (d in 2:73)  { 
    matplot (D[, 1], D[d], type='l', 
    xlab=NA,  xlim=c(0,500),
    ylab=NA, 
    log="y", 
    main=colnames(D)[d], #col=palette()[sample(1:8, 1)] 
    col="Red"
    )  
}


#prompt  <- "hit spacebar to close plots"
#extra   <- "some extra comment"
#capture <- tk_messageBox(message = prompt, detail = extra)
