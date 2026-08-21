function [p, K2] = dagostino_k2(x)
% Prueba de normalidad de D'Agostino-Pearson (K cuadrado).
% Junta la asimetria y la curtosis en un solo estadistico chi2 con 2 gl.
% Sirve como complemento de Shapiro-Wilk: dice *por que* falla la normalidad.
%
%   [p, K2] = dagostino_k2(x)

x = x(:); x = x(~isnan(x));
n = numel(x);
if n < 20
    p = NaN; K2 = NaN; return   % la aproximacion no es fiable con n chico
end

% --- parte de asimetria -> Z1
b1 = skewness(x, 1);
Y  = b1 * sqrt((n+1)*(n+3) / (6*(n-2)));
b2t = 3*(n^2 + 27*n - 70)*(n+1)*(n+3) / ((n-2)*(n+5)*(n+7)*(n+9));
W2 = -1 + sqrt(2*(b2t - 1));
del = 1 / sqrt(log(sqrt(W2)));
alf = sqrt(2/(W2 - 1));
Z1 = del * asinh(Y/alf);

% --- parte de curtosis -> Z2
b2  = kurtosis(x, 1);
Eb2 = 3*(n-1)/(n+1);
Vb2 = 24*n*(n-2)*(n-3) / ((n+1)^2*(n+3)*(n+5));
Xx  = (b2 - Eb2) / sqrt(Vb2);
sb1 = 6*(n^2 - 5*n + 2)/((n+7)*(n+9)) * sqrt(6*(n+3)*(n+5)/(n*(n-2)*(n-3)));
A   = 6 + 8/sb1 * (2/sb1 + sqrt(1 + 4/sb1^2));
Z2  = ((1 - 2/(9*A)) - ((1 - 2/A)/(1 + Xx*sqrt(2/(A-4))))^(1/3)) / sqrt(2/(9*A));

K2 = Z1^2 + Z2^2;
p  = chi2cdf(K2, 2, 'upper');
end
