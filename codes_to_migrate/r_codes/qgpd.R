# scipy.stats.genpareto.ppf(q, c, loc=0, scale=1)
#                           p, shape, loc, scale
qgpd = function (p, loc = 0, scale = 1, shape = 0, lower.tail = TRUE, 
          lambda = 0) {
  if (min(p, na.rm = TRUE) <= 0 || max(p, na.rm = TRUE) >= 
      1) 
    stop("`p' must contain probabilities in (0,1)")
  if (min(scale) < 0) 
    stop("invalid scale")
  if (length(shape) != 1) 
    stop("invalid shape")
  if ((lambda < 0) || (lambda >= 1) || length(lambda) != 1) 
    stop("invalid lambda")
  if (any(p < lambda)) 
    stop("``p'' must satisfy ``p >= lambda''")
  if (lower.tail) 
    p <- 1 - p
  p <- p/(1 - lambda)
  if (shape == 0) 
    return(loc - scale * log(p))
  else return(loc + scale * (p^(-shape) - 1)/shape)
}
