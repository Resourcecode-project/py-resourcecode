oversampling = function(S,n,fsamp=1){
  #  Over-sampling by Fourier-Inverse Fourier
  #
  #syntax : [SoS,time] = oversampling(S,n[,fsamp])
  #
  #
  #      I	- S	: time serie (vector or matrix)
  #      I 	- n	: over-sampling rate
  #      I	- fsamp	: sampling frequency (default = 1)
  #     O	- SoS	: over-sampled time serie (vector or matrix)
  #     O	- time	: instants time serie
  # 
  #  author : Marc PREVOSTO - IFREMER - 22 January 1997
  #  Conversion R: Nicolas RAILLARD - Janvier 2015
  if(n==1){
    SoS=S
    sS=dim(S)
    time = (0:(sS[1]-1))/fsamp
    return(list(SoS,time))
  }
  S=as.matrix(S)
  nl=dim(S)[1]
  nc=dim(S)[2]
  vl=0
  if(nl==1){
    S=t(S)
    vl=1
    nl=nc
    nc=1
  }
  z=matrix(0,nrow=round(nl*(n-1)),ncol=nc)
  
  odd = round(nl/2)==nl/2
  if(nc>1){
    SoS=mvfft(S)
    nc=floor(nl/2)
    if(odd){
      SoSc=SoS[nc+1,]/2
      z=z[-nrow(z),]
    }
    else{
      SoSc=SoS[nc+1,]
    }
    SoS = rbind(SoS[1:nc,],SoSc,z,Conj(SoSc),Conj(SoS[seq(from=nc,to=2,by=-1),]))
    nln = nrow(SoS)
    SoS = Re(mvfft(SoS,inverse = T))*(1/nl) #iff n'est pas normalisé dans R...
  }
  else{
    SoS=fft(S)
    nc=floor(nl/2)
    if(odd){
      SoSc=SoS[nc+1,]/2
      z=z[-nrow(z),]
    }
    else{
      SoSc=SoS[nc+1,]
    }
    SoS = c(SoS[1:nc,],SoSc,z,Conj(SoSc),Conj(SoS[seq(from=nc,to=2,by=-1),]))
    nln = length(SoS)
    SoS = Re(fft(SoS,inverse = T))*(1/nl) #iff n'est pas normalisé dans R...
  }
  
  if(vl==1){
    SoS=t(SoS)
  }
  time = (0:(nln-1))*(nl/fsamp/nln)
  return(list(SoS,time))
}