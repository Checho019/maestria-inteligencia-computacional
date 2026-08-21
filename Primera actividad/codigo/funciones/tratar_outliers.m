function [Xout, info] = tratar_outliers(X, cols, modo, factor)
% Trata los atipicos univariados con la regla de Tukey (1.5*IQR).
%
%   modo = 'winsor'   -> recorta el valor al limite (no se pierden filas)
%   modo = 'eliminar' -> marca las filas para borrarlas (info.filas_malas)
%
% Criterio que usamos: si el porcentaje de filas afectadas es alto,
% eliminar seria tirar demasiada informacion, asi que se winsoriza.
%
%   cols   -> indices de las columnas continuas a las que aplica la regla
%             (no tiene sentido aplicarsela a dummies o binarias)
%   factor -> 1.5 por defecto

if nargin < 4 || isempty(factor), factor = 1.5; end

Xout = X;
n = size(X, 1);
marca = false(n, 1);
det = zeros(numel(cols), 4);   % [n_atipicos, %, lim_inf, lim_sup]

for i = 1:numel(cols)
    j = cols(i);
    q = quantile(X(:, j), [0.25 0.75]);
    iqr_j = q(2) - q(1);

    % Si el IQR es 0 (mas del 75% de los datos en un mismo valor) la regla
    % de Tukey marcaria como atipico todo lo que no sea ese valor y al
    % winsorizar la variable quedaria constante. Mejor no tocarla.
    if iqr_j == 0
        det(i, :) = [0, 0, q(1), q(2)];
        continue
    end

    li = q(1) - factor*iqr_j;
    ls = q(2) + factor*iqr_j;
    fuera = X(:, j) < li | X(:, j) > ls;
    marca = marca | fuera;
    det(i, :) = [sum(fuera), 100*sum(fuera)/n, li, ls];
    if strcmp(modo, 'winsor')
        Xout(X(:, j) < li, j) = li;
        Xout(X(:, j) > ls, j) = ls;
    end
end

info.detalle      = det;
info.filas_malas  = marca;
info.pct_filas    = 100*sum(marca)/n;

if strcmp(modo, 'eliminar')
    Xout(marca, :) = [];
end
end
