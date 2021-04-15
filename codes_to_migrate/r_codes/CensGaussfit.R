#' Fit a censored Gaussian (Nataf) Copula to the data
#'
#' @param data 
#' @param quant 
#' @param method 
#'
#' @return
#' @export
#'
#' @examples
CensGaussfit = function(data,quant,method='optim'){

  nvar=ncol(data)
  us=apply(data,2,quantile,probs=quant)

  idx=TRUE
  for(i in 1:nvar){
    idx = idx & data[,i]>us[i] 
  }

  tail_dependency_obs = sum(idx)/nrow(data)
  th_norm=qnorm(quant)

  if(nvar==2){
    sigma=diag(nvar)
    sigma[1,2]<-sigma[2,1]<-cor(data[,1],data[,2])
  
    fitness=function(corg){
      sigma=diag(nvar)
      sigma[1,2]<-sigma[2,1]<-corg
      return((tail_dependency_obs-mvtnorm::pmvnorm(mean=0,sigma,lower = rep(th_norm,nvar),upper = Inf)[1])^2)
    }
    
    if(method=='exhaust'){
    xx=seq(from=0,to=1,length.out = 10000)
    ll=sapply(xx,fitness)
    #plot(xx,ll,type='l',col=Gcol[1])
    #abline(v=cor(data[,1],data[,2]),col=Gcol[2])
    return(xx[which.min(ll)])
    }
    else{
      return(optimize(fitness,c(0,1))$minimum)
    }
  }
  else{
    fitness=function(corg){
      sigma=diag(nvar)
      sigma[upper.tri(sigma)] <- corg
      sigma[lower.tri(sigma)] <- corg
      return((tail_dependency_obs-mvtnorm::pmvnorm(mean=0,sigma,lower = rep(th_norm,nvar),upper = Inf)[1])^2)
    }
    
    par0 = cor(data)[upper.tri(cor(data))]
    print(fitness(par0))
    return(optim(par0,fitness,lower = c(0,0,0),upper = c(1,1,1),method = "L-BFGS-B",
    control = list(
        parscale=rep(1000,nvar),
        factr=1e-10,
        fnscale=10^(-nvar)
    )))
    
  }
}
