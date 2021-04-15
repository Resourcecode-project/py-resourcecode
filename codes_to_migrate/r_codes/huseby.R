huseby = function(X,prob,ntheta=60,npt=ntheta,standard="biv",method=3,FORM=0){
#  huseby : contours in physical space
#
#syntax  : [X,Y,Z] = huseby(X,prob[,ntheta[,npt[,standard[,method[,FORM]]]]])
#
#      I   - X          : 2D [x,y] or 3D [x,y,z]
#      I   - prob     	: probability levels of the contours
#      I   - ntheta     : number of angles on [0,360] for calculation
#                           (ntheta must be a multiple of 4, default 60)
#      I   - npt     	: number of angles on [0,360] for output  npt>ntheta (default ntheta)
#                         it is adviced to take npt a multiple of ntheta
#      I   - standard   : 'none', 'univ' or 'biv' (normalisation method, default 'biv')
#      I   - method     : in 2D, 1 = consecutive straight line intersection
#                                2 = limit straight line intersection
#                                3 = closest straight line (default)
#                         in 3D, only 3 = closest plane
#      I   - FORM     	: number of Fourier components for smoothing (default 0)
#      O   - X      	: x contour (length of prob columns)
#      O   - Y      	: y contour (length of prob columns)
#      O   - Z      	: z contour (length of prob columns) (3D case)
#  author : Marc Prevosto - 22 December 2016
# R version: Nicolas Raillard, 17/07/2017

X=as.data.frame(X)

# normalisation
N = nrow(X)
if(standard!="none"){
  mX=apply(X,2,mean)
  sigma=apply(X,2,sd)
  X=scale(X)
}
if(standard=="biv"){
  Q = (t(X)%*%X)/(N-1)
  L = chol(Q)
  X = t(solve(t(L),t(X)))
}

#Calculs des quantiles
prob=as.vector(prob)
nprob = length(prob)
k = N*prob+0.5
kf = floor(k)
kc = ceiling(k)
dk = k-kf

#Calcul des angles
dthd = 360/ntheta
dth = dthd*(pi/180)
thetad = (0:(ntheta-1))*dthd
theta = thetad*(pi/180)
ctheta = cos(theta)
stheta = sin(theta)
dtheta = diff(theta)
sindtheta = sin(dtheta)
ntheta = length(theta)
noversamp = npt/ntheta

if(noversamp!=1){
  if(noversamp<1){noversamp = 10}
    else{noversamp = ceiling(noversamp)}
  thetadi1 = (0:(ntheta*noversamp-1))*(dthd/noversamp)
  thetadi = thetadi1
  if(noversamp!=(npt/ntheta)||noversamp<1){
          thetadi2 = (0:(npt-1))*360/npt
          thetadi = thetadi2
  }
  thetai = thetadi*(pi/180)
  cthetai = cos(thetai)
  sthetai = sin(thetai)
  nthetai = length(thetai)
  dthetai = diff(thetai)
  sindthetai = sin(dthetai)
  if(dim(X)[2]==3){indji = which(thetadi<=90|thetadi>=270)}
}

if(dim(X)[2]==2){
  C = matrix(1,ntheta,nprob)
  for(ii in 1:ntheta){
    Y = X%*%c(ctheta[ii],stheta[ii])
    Y = sort(Y)
    C[ii,] = t(Y[kc]-Y[kf])*dk+t(Y[kf])
  }
    if(method==3){
      ps = (ctheta%*%t(ctheta)+stheta%*%t(stheta))
      ps[ps<0]=0
      for(iprob in 1:nprob){
        temp=C[,iprob]
        temp=apply(matrix(temp,ntheta,ntheta)/ps,2,min)
        C[,iprob]=temp
      }
    }
    if(noversamp!=1){
      C = oversampling(C,noversamp,1/dthd)[[1]]
      if(noversamp!=npt/ntheta||noversamp<1){
        C = approx(thetadi1,C,thetadi2)}
      stheta = sthetai 
      ctheta = cthetai 
      dtheta = dthetai 
      sindtheta = sindthetai
    }
    if(method==1){
    X = (stheta[2:nrow(C)]*C[1:nrow(C)-1,]-stheta[1:nrow(C)-1]*C[2:nrow(C),])/sindtheta ;
    Y = (-ctheta[2:nrow(C)]*C[1:nrow(C)-1,]+ctheta[1:nrow(C)-1]*C[2:nrow(C),])/sindtheta
    }
    else if(method==2){
    Cp = fourfil(C,1/dtheta(1),0,inf,1)
    X = ctheta*C-stheta*Cp
    Y = ctheta*Cp+stheta*C
    }
    else if(method==3){
      X = ctheta*C
      Y = stheta*C
    }
    Y = (L[1,2]*sigma[2])*X+(L[2,2]*sigma[2])*Y+mX[2] ;
    X = (L[1,1]*sigma[1])*X+mX[1] ;
return(data.frame(X=X,Y=Y,theta=theta))
}
else if(dim(X)[2]==3){
  method = 3
  C=array(1,dim=c(ntheta,ntheta,nprob))
  indj=c(1:(ntheta/4+1),ntheta-(0:(ntheta/4-1)))
  nindj = ntheta/2+1 # on calcule entre -90 et 90
  icdir = 0
  ncdir = ntheta*nindj
  cdir = matrix(0,ncdir,3)
  Xres=matrix(NA,ncdir,nprob)
  Yres=matrix(NA,ncdir,nprob)
  Zres=matrix(NA,ncdir,nprob)
  for(ii in 1:ntheta){
    for(jj in indj){#on calcule entre -90 et 90
      #Rotation autour de Y de theta(ii), puis rotation autour de Z de -theta(jj)
      icdir = icdir+1
      cdirc = c(ctheta[ii]*ctheta[jj],stheta[jj],stheta[ii]*ctheta[jj])
      cdir[icdir,] = cdirc
      Y=X%*%cdirc
      Y = sort(Y)
      C[ii,jj,] = t(Y[kc]-Y[kf])*dk+Y[kf]
    }
  }
  if(method==3){
    ps = cdir%*%t(cdir)
    ps[ps<0]<-0
  }
  for(iprob in 1:nprob){
    temp=as.vector(t(C[,indj,iprob]))
    dmin = matrix(apply(rep(temp,ncdir)/ps,2,min),nindj,ntheta)
    C[,indj,iprob] = t(dmin)
    C[,(ntheta/4+2):(ntheta-ntheta/4),iprob] = C[c((ntheta/2+1):ntheta,1:(ntheta/2)),c(seq(from=ntheta/4,to=1,by=-1),ntheta-(0:(ntheta/4-2))),iprob]
    if(noversamp!=1){
      tempC = oversampling(t(C[,,iprob]),noversamp,1/dthd)[[1]]
      tempC = oversampling(t(tempC),noversamp,1/dthd)[[1]]
      if(noversamp!=npt/ntheta|noversamp<1){
        tempC = approx(thetadi1,tempC,thetadi2)
        tempC = approx(thetadi1,tempC,thetadi2)
      }
      tempX = (cthetai%*%t(cthetai[indji]))*tempC[,indji]
      tempY = t(matrix(sthetai[indji],nrow=length(indji),ncol=nthetai))*tempC[,indji]
      tempZ = (sthetai%*%t(cthetai[indji]))*tempC[,indji]
      if(iprob==1){
        Xres=matrix(tempX,ncol=1)
        Yres=matrix(tempY,ncol=1)
        Zres=matrix(tempZ,ncol=1)
      }
      else{
        Xres=cbind(Xres,as.vector(tempX))
        Yres=cbind(Yres,as.vector(tempY))
        Zres=cbind(Zres,as.vector(tempZ))
      }
    }
    else{
      temp = (ctheta%*%t(ctheta[indj]))*C[,indj,iprob]
      Xres[,iprob] = temp
      temp = t(matrix(stheta[indj],nrow=length(indj),ncol=ntheta))*C[,indj,iprob]
      Yres[,iprob] = temp
      temp = (stheta%*%t(ctheta[indj]))*C[,indj,iprob]
      Zres[,iprob] = temp
    }
        #Retour à l'échelle initialle
    Zres[,iprob]=(L[1,3]*sigma[3])*Xres[,iprob]+(L[2,3]*sigma[3])*Yres[,iprob]+(L[3,3]*sigma[3])*Zres[,iprob]+mX[3]
    Yres[,iprob]=(L[1,2]*sigma[2])*Xres[,iprob]+(L[2,2]*sigma[2])*Yres[,iprob]+mX[2]
    Xres[,iprob]=(L[1,1]*sigma[1])*Xres[,iprob]+mX[1]
  }
  return(data.frame(X=Xres,Y=Yres,Z=Zres,theta=theta))
}
}
