function vif = calcular_vif(X)
% Factor de inflacion de la varianza de cada columna de X.
% VIF_j = 1/(1-R2_j), donde R2_j es el R2 de regresar la columna j
% contra todas las demas. Regla practica: VIF > 5 ya huele a colinealidad,
% VIF > 10 es problema seguro.

p = size(X, 2);
vif = zeros(p, 1);
for j = 1:p
    otras = X(:, setdiff(1:p, j));
    otras = [ones(size(X,1),1) otras];          %#ok<AGROW>  intercepto
    yj = X(:, j);
    beta = otras \ yj;
    res  = yj - otras*beta;
    R2 = 1 - sum(res.^2) / sum((yj - mean(yj)).^2);
    vif(j) = 1 / max(1 - R2, 1e-12);
end
end
