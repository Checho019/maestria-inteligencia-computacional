function [p, W] = swtest(x)
% Prueba de normalidad de Shapiro-Wilk (algoritmo de Royston, 1992 - AS R94).
% MATLAB no la trae de fabrica, asi que la implementamos aqui porque el PDF
% de la guia la pide como primera opcion para muestras chicas/medianas.
%
%   [p, W] = swtest(x)
%   x -> vector de datos (se ignoran los NaN)
%   W -> estadistico de Shapiro-Wilk (cerca de 1 = parece normal)
%   p -> p-valor. Si p < 0.05 se rechaza la normalidad.
%
% Valida para 3 <= n <= 5000 aprox. Con n mas grande usar lillietest.

x = x(:);
x = x(~isnan(x));
x = sort(x);
n = numel(x);

if n < 3
    p = NaN; W = NaN; return
end

% valores esperados de los estadisticos de orden de una normal (aprox. Blom)
m = norminv(((1:n)' - 0.375) / (n + 0.25));
c = m / sqrt(m' * m);
u = 1 / sqrt(n);

% los pesos de las colas se corrigen con los polinomios de Royston
a = c;
a(n) = polyval([-2.706056 4.434685 -2.071190 -0.147981 0.221157 c(n)], u);
a(1) = -a(n);

if n > 5
    a(n-1) = polyval([-3.582633 5.682633 -1.752461 -0.293762 0.042981 c(n-1)], u);
    a(2)   = -a(n-1);
    phi = (m'*m - 2*m(n)^2 - 2*m(n-1)^2) / (1 - 2*a(n)^2 - 2*a(n-1)^2);
    medio = 3:(n-2);
else
    phi = (m'*m - 2*m(n)^2) / (1 - 2*a(n)^2);
    medio = 2:(n-1);
end
a(medio) = m(medio) / sqrt(phi);

W = (a' * x)^2 / sum((x - mean(x)).^2);

% transformacion a normal para sacar el p-valor (tres tramos segun n)
if n == 3
    p = max(0, min(1, 6/pi * (asin(sqrt(W)) - asin(sqrt(0.75)))));
elseif n <= 11
    gama = polyval([0.459 -2.273], n);
    mu   = polyval([-0.0006714 0.025054 -0.39978 0.5440], n);
    sg   = exp(polyval([-0.0020322 0.062767 -0.77857 1.3822], n));
    z = (-log(gama - log(1 - W)) - mu) / sg;
    p = normcdf(-z);   % normcdf(-z) en vez de 1-normcdf(z) para no perder precision
else
    ln = log(n);
    mu = polyval([0.0038915 -0.083751 -0.31082 -1.5861], ln);
    sg = exp(polyval([0.0030302 -0.082676 -0.4803], ln));
    z = (log(1 - W) - mu) / sg;
    p = normcdf(-z);   % normcdf(-z) en vez de 1-normcdf(z) para no perder precision
end
end
