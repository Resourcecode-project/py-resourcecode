#' Simulate from a fitted Nataf model
#'
#' @param rho Estimated correlation coefficient from censored Nataf Copulas, output from CensGaussfit
#' @param quant Quantile used for conditioning
#' @param GPD_param Estimated Threshold and GDP parameters (nvar * 3 matrix)
#' @param nsim Requested number of simulations
#'
#' @return
#' @export
#'
#' @examples
nataf_sim = function(nataf,quant,GPD_param,nsim){

  nvar = length(nataf)
  
	sigma=diag(nvar)
	sigma[upper.tri(sigma)] <- nataf
	sigma[lower.tri(sigma)] <- nataf
	
  X=NULL
	
	while(NROW(X)<nsim){

    # remplacer rmvn par scipy.multivariate_normal
	Xnew=as.data.frame(mvnfast::rmvn(nsim,mu=rep(0,nvar),sigma = sigma))
  names(Xnew)= c("V1","V2","V3") 
	
  Xnew=subset(Xnew,V1>qnorm(quant) & V2>qnorm(quant) & V3>qnorm(quant))
  
  Xnew$V1 = qgpd((pnorm(Xnew$V1)-quant)/(1-quant),loc=GPD_param[1,1], scale =  GPD_param[1,2], shape = GPD_param[1,3])
  Xnew$V2 = qgpd((pnorm(Xnew$V2)-quant)/(1-quant),loc=GPD_param[2,1], scale =  GPD_param[2,2], shape = GPD_param[2,3])
  Xnew$V3 = qgpd((pnorm(Xnew$V3)-quant)/(1-quant),loc=GPD_param[3,1], scale =  GPD_param[3,2], shape = GPD_param[3,3])
	
	X=rbind(X,Xnew)
	row.names(X) = NULL
	}
  
  return(X[1:nsim,])
}
