function Xnew = smote_simple(X, n_nuevos, k)
% SMOTE basico: crea n_nuevos ejemplos sinteticos interpolando cada punto
% con uno de sus k vecinos mas cercanos DENTRO de la misma clase.
% Solo tiene sentido con variables continuas.
%
% MATLAB no trae smote, asi que va esta version corta.

if nargin < 3, k = 5; end
n = size(X, 1);
k = min(k, n-1);

if n < 2 || n_nuevos <= 0
    Xnew = zeros(0, size(X,2));
    return
end

% vecinos: la primera columna es el propio punto, por eso pedimos k+1
idx = knnsearch(X, X, 'K', k+1);
idx = idx(:, 2:end);

base   = randi(n, n_nuevos, 1);                  % punto de partida
vecino = idx(sub2ind(size(idx), base, randi(k, n_nuevos, 1)));
lambda = rand(n_nuevos, 1);

Xnew = X(base, :) + lambda .* (X(vecino, :) - X(base, :));
end
