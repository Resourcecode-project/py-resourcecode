source("CensGaussfit.R")
source("nataf_sim.R")
source("qgpd.R")
source("huseby.R")

#Simulation parameters

# The following lines have been used to generate data. The output is saved and
# reused after

# rho = c(.2,.9999,.5)
# sigma=diag(c(1,3,2))
# sigma[upper.tri(sigma)] <- rho
# sigma[lower.tri(sigma)] <- rho
#
# #Simulation
# X = mvnfast::rmvt(1e6,mu=c(0,0,0),sigma = sigma, df=5)
# write.csv(X, "cengaussfit_data.csv")

X = read.csv("cengaussfit_data.csv", colClasses=c("NULL", NA, NA, NA))

#Estimation of thresholds and marginal parameters
quant = .9

par1 = extRemes::fevd(X[,1],threshold = quantile(X[,1],quant),type = "GP", method="MLE")
par2 = extRemes::fevd(X[,2],threshold = quantile(X[,2],quant),type = "GP")
par3 = extRemes::fevd(X[,3],threshold = quantile(X[,3],quant),type = "GP")

#Estimation of dependance structure
nataf = CensGaussfit(X,.9)
write.csv(nataf$par, "censgauss_fit.csv")

par = rbind(c(quantile(X[,1],quant),par1$results$par),
            c(quantile(X[,2],quant),par2$results$par),
            c(quantile(X[,3],quant),par3$results$par)
            )

#Simulation from the fitted model
sim = nataf_sim(nataf = nataf$par,quant = quant,GPD_param = par,nsim = 10000)
# write.csv(sim, "nataf_simulation.csv")

sim = read.csv("nataf_simulation.csv", colClasses=c("NULL", NA, NA, NA))

#Estimation of contours with the method from Huseby
contours = huseby(sim,c(.9,.95,.975),ntheta = 120,npt = 120)

plot3D::lines3D(contours[,3],contours[,6],contours[,9],col='red')
plot3D::lines3D(contours[,1],contours[,4],contours[,7],col='green',add=T)
plot3D::lines3D(contours[,3],contours[,6],contours[,8],col='blue',add=T)

write.csv(contours, "huseby.csv")
